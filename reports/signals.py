# reports/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import IssueReport
from .utils import generate_report_number, send_email_notification

# Auto-create user profile when User is created
@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            from FreeContribution.models import UserProfile
            # Create a minimal profile; user will complete later
            UserProfile.objects.get_or_create(user=instance, defaults={
                "phone_number": "9999999999",  # placeholder to avoid validation at creation
                "postal_code": "380000",       # placeholder
                "address": "",
                "is_verified": True,
            })
        except (ImportError, AttributeError):
            # UserProfile model doesn't exist, skip
            pass

# Pre-save: generate report number if blank, store original status for change detection
@receiver(pre_save, sender=IssueReport)
def issue_presave(sender, instance: IssueReport, **kwargs):
    if not instance.report_number:
        instance.report_number = generate_report_number()
    # snapshot original status for post_save comparison
    if instance.pk:
        try:
            old = IssueReport.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except IssueReport.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

# Post-save: update user stats and send notification on status change
@receiver(post_save, sender=IssueReport)
def issue_postsave(sender, instance: IssueReport, created, **kwargs):
    # Update total_reports
    try:
        profile = getattr(instance.user, "profile", None)
        if profile and created and hasattr(profile, "total_reports"):
            profile.total_reports += 1
            if hasattr(profile, "updated_at"):
                profile.save(update_fields=["total_reports", "updated_at"])
            else:
                profile.save(update_fields=["total_reports"])
    except Exception:
        pass

    # Status change email + reputation
    old_status = getattr(instance, "_old_status", None)
    if old_status and old_status != instance.status:
        if instance.status == "APPROVED":
            send_email_notification(instance, "approved")
        elif instance.status == "RESOLVED":
            send_email_notification(instance, "resolved")
            # reward reputation
            try:
                profile = getattr(instance.user, "profile", None)
                if profile and hasattr(profile, "increment_valid_report"):
                    profile.increment_valid_report(+10)
            except Exception:
                pass
        elif instance.status == "REJECTED" and instance.is_spam:
            send_email_notification(instance, "rejected")
            try:
                profile = getattr(instance.user, "profile", None)
                if profile and hasattr(profile, "increment_spam_count"):
                    profile.increment_spam_count(-10)
            except Exception:
                pass

    # On create, send submitted email
    if created:
        send_email_notification(instance, "submitted")