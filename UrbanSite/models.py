# UrbanSite/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Authority(models.Model):
    """
    Represents a municipal authority/department that handles reports.
    """
    name = models.CharField(max_length=200, help_text="Name of the authority/department")
    email = models.EmailField(help_text="Contact email for this authority")
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        help_text="Contact phone number"
    )
    area = models.CharField(max_length=100, help_text="Area/ward covered by this authority")
    department = models.CharField(max_length=100, help_text="Department name (e.g., Roads, Water, Sanitation)")
    is_active = models.BooleanField(default=True, help_text="Whether this authority is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'UrbanSite'
        verbose_name = "Authority"
        verbose_name_plural = "Authorities"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.department}"


class UserReport(models.Model):
    """
    User-submitted civic issue reports.
    """
    PROBLEM_TYPE_CHOICES = [
        ('Roads', 'Roads & Infrastructure'),
        ('Water', 'Water Supply'),
        ('Sanitation', 'Sanitation & Waste'),
        ('Electricity', 'Electricity'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]

    # User information
    name = models.CharField(max_length=200, help_text="Reporter's full name")
    email = models.EmailField(help_text="Reporter's email address")
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'.")],
        help_text="Reporter's phone number"
    )

    # Location information
    area = models.CharField(max_length=100, help_text="Area/ward name")
    pincode = models.CharField(
        max_length=6,
        validators=[RegexValidator(regex=r'^\d{6}$', message="Pincode must be exactly 6 digits.")],
        help_text="6-digit pincode",
        db_index=True
    )
    address = models.TextField(blank=True, help_text="Detailed address (optional)")

    # Report details
    problem_type = models.CharField(
        max_length=50,
        choices=PROBLEM_TYPE_CHOICES,
        default='Other',
        help_text="Type of problem"
    )
    description = models.TextField(help_text="Detailed description of the issue")
    image = models.ImageField(
        upload_to='reports/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Photo of the issue (optional)"
    )

    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        db_index=True
    )
    authority = models.ForeignKey(
        Authority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports',
        help_text="Assigned authority"
    )

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of submitter")
    user_agent = models.CharField(max_length=500, blank=True, help_text="User agent string")

    class Meta:
        app_label = 'UrbanSite'
        ordering = ['-timestamp']
        verbose_name = "User Report"
        verbose_name_plural = "User Reports"
        indexes = [
            models.Index(fields=['pincode', '-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.name} - {self.problem_type} ({self.area}) - {self.timestamp.strftime('%Y-%m-%d')}"

    def mark_resolved(self):
        """Mark the report as resolved."""
        self.status = 'Resolved'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at', 'updated_at'])


class Feedback(models.Model):
    """
    Feedback/response from authority regarding a report.
    """
    report = models.ForeignKey(
        UserReport,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text="Associated report"
    )
    authority = models.ForeignKey(
        Authority,
        on_delete=models.SET_NULL,
        null=True,
        related_name='feedbacks',
        help_text="Authority providing feedback"
    )
    message = models.TextField(help_text="Feedback message")
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this feedback should be visible to the reporter"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'UrbanSite'
        ordering = ['-created_at']
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"Feedback for Report #{self.report.id} - {self.created_at.strftime('%Y-%m-%d')}"
