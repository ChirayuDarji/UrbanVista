# reports/notifications.py
"""
Email notification utilities for report status changes.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_report_status_notification(report, old_status, new_status, changed_by=None):
    """
    Send email notification to report owner when status changes.
    
    Args:
        report: Report instance
        old_status: Previous status
        new_status: New status
        changed_by: User who made the change (optional)
    """
    if not report.user.email:
        return  # No email to send to
    
    # Status change messages
    status_messages = {
        'pending': 'Your report has been submitted and is pending review.',
        'assigned': 'Your report has been assigned to a department.',
        'in_progress': 'Work has started on your report.',
        'resolved': 'Your report has been resolved!',
        'rejected': 'Your report has been rejected.',
    }
    
    subject = f"Report Status Update: {report.get_status_display()}"
    message = status_messages.get(new_status, f'Your report status has been updated to {report.get_status_display()}.')
    
    # Build email content
    context = {
        'report': report,
        'old_status': old_status,
        'new_status': new_status,
        'status_display': report.get_status_display(),
        'message': message,
        'changed_by': changed_by,
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }
    
    # Try to render HTML email template, fallback to plain text
    try:
        html_message = render_to_string('reports/emails/status_change.html', context)
    except:
        html_message = None
    
    plain_message = f"""
Hello {report.user.get_full_name() or report.user.username},

{message}

Report Details:
- Issue Type: {report.get_issue_type_display()}
- Location: {report.location}
- Status: {report.get_status_display()}
- Report ID: #{report.pk}

View your report: {context['site_url']}/reports/{report.pk}/

Thank you for using UrbanVista!
"""
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[report.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        # Log error but don't break the flow
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email notification for report {report.pk}: {str(e)}")

