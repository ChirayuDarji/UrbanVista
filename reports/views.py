# reports/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count, Q, Avg, Sum, F
from django.db.models.functions import TruncMonth, TruncYear, TruncDay
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta
import json
from .models import Report, ReportAttachment, ReportStatusHistory
from .forms import (
    ReportForm,
    ReportAttachmentForm,
    ReportStatusUpdateForm,
    ReportFeedbackForm,
)

# Utility: Check if user is staff/authority
def is_authority(user):
    return user.is_staff or user.groups.filter(name='Authority').exists()

# 1. List all reports submitted by the current user
@login_required
def report_list(request):
    reports = Report.objects.filter(user=request.user).select_related('department', 'user').prefetch_related('attachments').order_by('-created_at')
    return render(request, 'reports/report_list.html', {'reports': reports})

# 2. View details of a single report (owner or staff/authority can view)
@login_required
def report_detail(request, pk):
    report = get_object_or_404(
        Report.objects.select_related('department', 'user', 'assigned_to').prefetch_related('status_history', 'attachments'),
        pk=pk
    )
    # Only owner or authority can view
    if report.user != request.user and not is_authority(request.user):
        messages.error(request, "You do not have permission to view this report.")
        return redirect('reports:report_list')

    # Show status history and attachments (already prefetched)
    status_history = report.status_history.all()
    attachments = report.attachments.all()

    # Feedback form (only if resolved and user is owner and no feedback yet)
    feedback_form = None
    if report.is_resolved() and report.user == request.user and not report.feedback:
        if request.method == 'POST' and 'feedback_submit' in request.POST:
            feedback_form = ReportFeedbackForm(request.POST, instance=report)
            if feedback_form.is_valid():
                feedback_form.save()
                messages.success(request, "Thank you for your feedback!")
                return redirect('reports:report_detail', pk=report.pk)
        else:
            feedback_form = ReportFeedbackForm(instance=report)

    # Status update form (for authority)
    status_form = None
    if is_authority(request.user):
        if request.method == 'POST' and 'status_update' in request.POST:
            status_form = ReportStatusUpdateForm(request.POST, instance=report)
            if status_form.is_valid():
                old_status = report.status
                updated_report = status_form.save(commit=False)
                updated_report.last_updated_by = request.user
                updated_report.save()
                # Log status change
                if old_status != updated_report.status:
                    ReportStatusHistory.objects.create(
                        report=report,
                        old_status=old_status,
                        new_status=updated_report.status,
                        changed_by=request.user,
                        remarks=request.POST.get('remarks', '')
                    )
                    # Send email notification
                    try:
                        from .notifications import send_report_status_notification
                        send_report_status_notification(
                            report=updated_report,
                            old_status=old_status,
                            new_status=updated_report.status,
                            changed_by=request.user
                        )
                    except Exception as e:
                        # Log but don't break the flow
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Failed to send notification: {str(e)}")
                messages.success(request, "Report status updated.")
                return redirect('reports:report_detail', pk=report.pk)
        else:
            status_form = ReportStatusUpdateForm(instance=report)

    context = {
        'report': report,
        'status_history': status_history,
        'attachments': attachments,
        'feedback_form': feedback_form,
        'status_form': status_form,
    }
    return render(request, 'reports/report_detail.html', context)

# 3. Submit a new report (with multiple attachments)
from core.decorators import rate_limit


@login_required
@rate_limit("report_create", limit=5, window_seconds=60)
def report_create(request):
    try:
        if request.method == 'POST':
            form = ReportForm(request.POST, request.FILES)
            if form.is_valid():
                new_report = form.save(commit=False)
                new_report.user = request.user
                new_report.city = "Ahmedabad"  # Or get from user profile if multi-city
                new_report.save()
                # Save attachments
                try:
                    files = request.FILES.getlist('attachments')
                    for f in files:
                        ReportAttachment.objects.create(report=new_report, file=f, uploaded_by=request.user)
                except Exception as e:
                    # Log error but continue
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error saving attachments for report {new_report.pk}: {str(e)}")
                messages.success(request, "Your report has been submitted successfully!")
                return redirect('reports:report_list')
        else:
            form = ReportForm()
        return render(request, 'reports/report_form.html', {'form': form})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in report_create view: {str(e)}")
        messages.error(request, "An error occurred while submitting your report. Please try again.")
        form = ReportForm()
        return render(request, 'reports/report_form.html', {'form': form})

# 4. Edit a report (only if status is pending and user is owner)
@login_required
def report_edit(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if report.user != request.user or report.status != 'pending':
        messages.error(request, "You can only edit your own pending reports.")
        return redirect('reports:report_list')
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            # Handle new attachments if any
            files = request.FILES.getlist('attachments')
            for f in files:
                ReportAttachment.objects.create(report=report, file=f, uploaded_by=request.user)
            messages.success(request, "Your report has been updated.")
            return redirect('reports:report_detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
    attachments = report.attachments.all()
    return render(request, 'reports/report_form.html', {'form': form, 'attachments': attachments, 'edit_mode': True})

# 5. Delete a report (only if status is pending and user is owner)
@login_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if report.user != request.user or report.status != 'pending':
        messages.error(request, "You can only delete your own pending reports.")
        return redirect('reports:report_list')
    if request.method == 'POST':
        report.delete()
        messages.success(request, "Your report has been deleted.")
        return redirect('reports:report_list')
    return render(request, 'reports/report_confirm_delete.html', {'report': report})

# 6. (Optional) Upload additional attachments (for staff or owner)
@login_required
def report_add_attachment(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if report.user != request.user and not is_authority(request.user):
        messages.error(request, "You do not have permission to add attachments.")
        return redirect('reports:report_detail', pk=report.pk)
    if request.method == 'POST':
        form = ReportAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.report = report
            attachment.uploaded_by = request.user
            attachment.save()
            messages.success(request, "Attachment uploaded.")
            return redirect('reports:report_detail', pk=report.pk)
    else:
        form = ReportAttachmentForm()
    return render(request, 'reports/report_add_attachment.html', {'form': form, 'report': report})

# ========================================
# NEW FEATURES - NO DATABASE CHANGES
# ========================================

# 1. Statistics & Analytics Dashboard
@cache_page(60 * 5)  # Cache for 5 minutes
def statistics_dashboard(request):
    """Statistics dashboard with charts and analytics."""
    from django.utils import timezone
    from datetime import timedelta
    
    # Overall stats
    total_reports = Report.objects.count()
    resolved_reports = Report.objects.filter(status='resolved').count()
    pending_reports = Report.objects.filter(status='pending').count()
    in_progress_reports = Report.objects.filter(status='in_progress').count()
    
    # Resolution rate
    resolution_rate = (resolved_reports / total_reports * 100) if total_reports > 0 else 0
    
    # Reports by status
    status_counts = Report.objects.values('status').annotate(count=Count('id')).order_by('status')
    status_data = {item['status']: item['count'] for item in status_counts}
    
    # Reports by category
    category_counts = Report.objects.values('issue_type').annotate(count=Count('id')).order_by('-count')
    category_data = {item['issue_type']: item['count'] for item in category_counts}
    
    # Monthly trends (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    monthly_data = Report.objects.filter(created_at__gte=twelve_months_ago).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Daily reports (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_data = Report.objects.filter(created_at__gte=thirty_days_ago).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Average resolution time (for resolved reports)
    resolved_with_times = Report.objects.filter(
        status='resolved',
        created_at__isnull=False,
        updated_at__isnull=False
    )
    avg_resolution_days = None
    if resolved_with_times.exists():
        total_seconds = sum(
            (r.updated_at - r.created_at).total_seconds() 
            for r in resolved_with_times
        )
        avg_seconds = total_seconds / resolved_with_times.count()
        avg_resolution_days = round(avg_seconds / 86400, 1)  # Convert to days
    
    # Top locations
    top_locations = Report.objects.values('location').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Convert datetime objects to strings for JSON serialization
    monthly_data_json = []
    for item in monthly_data:
        monthly_data_json.append({
            'month': item['month'].strftime('%Y-%m-%d') if item['month'] else '',
            'count': item['count']
        })
    
    daily_data_json = []
    for item in daily_data:
        daily_data_json.append({
            'day': item['day'].strftime('%Y-%m-%d') if item['day'] else '',
            'count': item['count']
        })
    
    context = {
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'resolution_rate': round(resolution_rate, 1),
        'status_data': mark_safe(json.dumps(status_data)),
        'category_data': mark_safe(json.dumps(category_data)),
        'monthly_data': mark_safe(json.dumps(monthly_data_json)),
        'daily_data': mark_safe(json.dumps(daily_data_json)),
        'avg_resolution_days': avg_resolution_days,
        'top_locations': top_locations,
    }
    return render(request, 'reports/statistics_dashboard.html', context)

# 2. Leaderboard & Rankings
@cache_page(60 * 5)  # Cache for 5 minutes
def leaderboard(request):
    """Leaderboard showing top contributors."""
    # Top contributors (most reports)
    top_contributors = Report.objects.values(
        'user__id', 'user__username', 'user__first_name', 'user__last_name'
    ).annotate(
        total_reports=Count('id'),
        resolved_reports=Count('id', filter=Q(status='resolved')),
        pending_reports=Count('id', filter=Q(status='pending'))
    ).order_by('-total_reports')[:50]
    
    # Most resolved (users with highest resolution rate)
    users_with_reports = Report.objects.values('user__id').annotate(
        total=Count('id')
    ).filter(total__gte=5)  # At least 5 reports
    
    most_resolved = []
    for user_data in users_with_reports:
        user_id = user_data['user__id']
        user_reports = Report.objects.filter(user_id=user_id)
        total = user_reports.count()
        resolved = user_reports.filter(status='resolved').count()
        if total > 0:
            resolution_rate = (resolved / total) * 100
            user = user_reports.first().user
            most_resolved.append({
                'user': user,
                'total': total,
                'resolved': resolved,
                'resolution_rate': round(resolution_rate, 1)
            })
    
    most_resolved.sort(key=lambda x: x['resolution_rate'], reverse=True)
    most_resolved = most_resolved[:20]
    
    # Active this month
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    active_this_month = Report.objects.filter(
        created_at__gte=this_month_start
    ).values(
        'user__id', 'user__username', 'user__first_name', 'user__last_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:20]
    
    context = {
        'top_contributors': top_contributors,
        'most_resolved': most_resolved,
        'active_this_month': active_this_month,
    }
    return render(request, 'reports/leaderboard.html', context)

# 3. Enhanced User Dashboard
@login_required
def enhanced_dashboard(request):
    """Enhanced user dashboard with stats and timeline."""
    user_reports = Report.objects.filter(user=request.user)
    
    # User stats
    total = user_reports.count()
    resolved = user_reports.filter(status='resolved').count()
    pending = user_reports.filter(status='pending').count()
    in_progress = user_reports.filter(status='in_progress').count()
    rejected = user_reports.filter(status='rejected').count()
    
    # Resolution rate
    user_resolution_rate = (resolved / total * 100) if total > 0 else 0
    
    # Recent reports
    recent_reports = user_reports.order_by('-created_at')[:10]
    
    # Activity timeline (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    activity_timeline = user_reports.filter(
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')
    
    # Reports by category
    user_category_counts = user_reports.values('issue_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly activity (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_activity = user_reports.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    # Convert monthly activity to JSON
    monthly_activity_json = []
    for item in monthly_activity:
        monthly_activity_json.append({
            'month': item['month'].strftime('%Y-%m-%d') if item['month'] else '',
            'count': item['count']
        })
    
    context = {
        'total': total,
        'resolved': resolved,
        'pending': pending,
        'in_progress': in_progress,
        'rejected': rejected,
        'resolution_rate': round(user_resolution_rate, 1),
        'recent_reports': recent_reports,
        'activity_timeline': activity_timeline,
        'category_counts': user_category_counts,
        'monthly_activity': mark_safe(json.dumps(monthly_activity_json)),
    }
    return render(request, 'reports/enhanced_dashboard.html', context)
