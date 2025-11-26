# reports/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import IssueReport

def generate_report_number():
    year = timezone.now().year
    prefix = f"AHM-{year}-"
    year_count = IssueReport.objects.filter(submitted_at__year=year).count() + 1
    base = f"{prefix}{year_count:05d}"
    while IssueReport.objects.filter(report_number=base).exists():
        year_count += 1
        base = f"{prefix}{year_count:05d}"
    return base

def get_user_stats(user):
    """Get statistics for a user's reports."""
    qs = IssueReport.objects.filter(user=user)
    profile = getattr(user, "profile", None)
    reputation = 0
    if profile:
        reputation = getattr(profile, "reputation_score", 0)
    return {
        "total": qs.count(),
        "resolved": qs.filter(status="RESOLVED").count(),
        "pending": qs.filter(status="PENDING").count(),
        "approved": qs.filter(status="APPROVED").count(),
        "in_progress": qs.filter(status="IN_PROGRESS").count(),
        "spam": qs.filter(is_spam=True).count(),
        "reputation": reputation,
    }

def send_email_notification(report: IssueReport, email_type: str):
    subjects = {
        "submitted": f"Report Submitted - {report.report_number}",
        "approved": f"Report Approved - {report.report_number}",
        "resolved": f"Issue Resolved - {report.report_number}",
        "rejected": f"Report Update - {report.report_number}",
    }
    templates = {
        "submitted": "emails/report_submitted.html",
        "approved": "emails/report_approved.html",
        "resolved": "emails/report_resolved.html",
        "rejected": "emails/report_rejected.html",
    }
    subject = subjects.get(email_type, f"Report Update - {report.report_number}")
    template = templates.get(email_type, "emails/report_submitted.html")

    ctx = {"report": report, "user": report.user}
    try:
        message_html = render_to_string(template, ctx)
        message_plain = render_to_string(template, ctx)
    except Exception:
        # Fallback if template missing
        message_html = f"<p>{subject}</p>"
        message_plain = subject

    try:
        send_mail(
            subject=subject,
            message=message_plain,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@urbansite.local"),
            recipient_list=[report.user.email] if report.user.email else [],
            html_message=message_html,
            fail_silently=True,
        )
    except Exception:
        pass