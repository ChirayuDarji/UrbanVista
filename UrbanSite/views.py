# UrbanSite/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import logging
from .models import UserReport, Authority
from .forms import UserReportForm
from .security import (
    get_client_ip,
    check_rate_limit as security_check_rate_limit,
    validate_content_for_spam
)

# Get logger for security events
logger = logging.getLogger('UrbanSite')


# Legacy rate limiting tracker (kept for backward compatibility)
# New code should use security.check_rate_limit with Django cache
submission_tracker = {}


def find_matching_authority(area, problem_type):
    """
    Find the appropriate authority for a given area and problem type.
    This is a simple matching logic - can be enhanced with better mapping.
    """
    # Try to find authority by area and department
    department_mapping = {
        'Roads': 'Roads',
        'Water': 'Water Supply',
        'Sanitation': 'Sanitation',
        'Electricity': 'Electricity',
        'Other': 'General',
    }
    
    department = department_mapping.get(problem_type, 'General')
    
    # Try exact match first
    authority = Authority.objects.filter(
        area__icontains=area,
        department__icontains=department,
        is_active=True
    ).first()
    
    # Fallback: match by area only
    if not authority:
        authority = Authority.objects.filter(
            area__icontains=area,
            is_active=True
        ).first()
    
    # Fallback: match by department only
    if not authority:
        authority = Authority.objects.filter(
            department__icontains=department,
            is_active=True
        ).first()
    
    # Final fallback: any active authority
    if not authority:
        authority = Authority.objects.filter(is_active=True).first()
    
    return authority


def send_report_email(report, authority):
    """
    Send email notification to the assigned authority.
    """
    if not authority or not authority.email:
        return False
    
    subject = f"New Civic Issue Report - {report.problem_type} in {report.area}"
    
    message = f"""
A new civic issue has been reported:

Reporter Details:
- Name: {report.name}
- Email: {report.email}
- Phone: {report.phone}

Location:
- Area: {report.area}
- Pincode: {report.pincode}
- Address: {report.address or 'Not provided'}

Issue Details:
- Type: {report.get_problem_type_display()}
- Description: {report.description}

Report ID: #{report.id}
Submitted: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Please review and take appropriate action.

---
This is an automated message from UrbanSite.
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [authority.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log error but don't fail silently in production
        # In tests, this will be caught by the test framework
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending email: {e}")
        return False


def report_issue(request):
    """
    Handle report submission form (GET: show form, POST: process submission).
    """
    if request.method == 'POST':
        form = UserReportForm(request.POST, request.FILES, request=request)
        
        if form.is_valid():
            # Rate limiting check using Django cache (more robust)
            ip_address = get_client_ip(request)
            email = form.cleaned_data.get('email', '')
            
            # Check rate limit by IP
            is_allowed_ip, time_remaining_ip = security_check_rate_limit(
                ip_address, 
                max_requests=1, 
                time_window=300,  # 5 minutes
                action="report_submission"
            )
            
            # Also check by email to prevent same user submitting multiple times
            is_allowed_email, time_remaining_email = security_check_rate_limit(
                email,
                max_requests=1,
                time_window=300,
                action="report_submission"
            )
            
            if not is_allowed_ip:
                logger.warning(
                    f"Rate limit exceeded for IP: {ip_address}",
                    extra={'ip_address': ip_address, 'action': 'report_submission'}
                )
                messages.error(
                    request,
                    f"Rate limit exceeded. Please wait {int(time_remaining_ip/60)} minutes before submitting another report."
                )
                return render(request, 'UrbanSite/report_form.html', {'form': form})
            
            if not is_allowed_email:
                logger.warning(
                    f"Rate limit exceeded for email: {email}",
                    extra={'email': email, 'action': 'report_submission'}
                )
                messages.error(
                    request,
                    f"Rate limit exceeded for this email address. Please wait {int(time_remaining_email/60)} minutes before submitting another report."
                )
                return render(request, 'UrbanSite/report_form.html', {'form': form})
            
            # Create report
            report = form.save(commit=False)
            report.ip_address = ip_address
            report.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Find matching authority
            authority = find_matching_authority(report.area, report.problem_type)
            if authority:
                report.authority = authority
            
            report.save()
            
            # Rate limit is handled by Django cache in security module
            # Log successful submission
            logger.info(
                f"Report submitted successfully: ID={report.id}, IP={ip_address}, Email={report.email}",
                extra={'report_id': report.id, 'ip_address': ip_address}
            )
            
            # Send email notification
            if authority:
                email_sent = send_report_email(report, authority)
                if email_sent:
                    print(f"Email sent to {authority.email} for report #{report.id}")
                else:
                    print(f"Failed to send email for report #{report.id}")
            
            # Redirect to success page
            return redirect('urbansite:success', report_id=report.pk)
        else:
            # Form validation failed
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserReportForm(request=request)
    
    return render(request, 'UrbanSite/report_form.html', {
        'form': form,
        'title': 'Report Civic Issue',
    })


def success(request, report_id):
    """
    Success page after report submission.
    """
    try:
        report = UserReport.objects.get(pk=report_id)
    except UserReport.DoesNotExist:
        messages.error(request, "Report not found.")
        return redirect('urbansite:report_issue')
    
    context = {
        'report': report,
        'title': 'Report Submitted Successfully',
    }
    return render(request, 'UrbanSite/success.html', context)


def not_allowed(request):
    """
    Page shown when user tries to submit from outside Ahmedabad.
    """
    context = {
        'title': 'Reporting Not Available',
    }
    return render(request, 'UrbanSite/not_allowed.html', context)
