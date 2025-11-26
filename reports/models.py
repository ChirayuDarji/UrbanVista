# reports/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Department(models.Model):
    """
    Represents a civic department (e.g., Roads, Sanitation, Water).
    """
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name

class Report(models.Model):
    """
    Model representing a civic issue reported by a citizen.
    """

    # Choices for issue types
    ISSUE_TYPE_CHOICES = [
        ('road', 'Road/Pothole'),
        ('garbage', 'Garbage'),
        ('water', 'Water Leakage'),
        ('streetlight', 'Broken Streetlight'),
        ('sewage', 'Sewage/Drainage'),
        ('other', 'Other'),
    ]

    # Choices for report status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    # The user who submitted the report
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        help_text="Citizen who submitted the report"
    )

    # Type of civic issue
    issue_type = models.CharField(
        max_length=20,
        choices=ISSUE_TYPE_CHOICES,
        help_text="Category of the reported issue"
    )

    other_issue = models.CharField(
    max_length=255,
    blank=True,
    null=True,
    help_text="If issue type is 'Other', specify here."
)
    
    # Short description of the problem
    description = models.TextField(
        help_text="Detailed description of the issue"
    )

    # Location as text (e.g., area, landmark, or address)
    location = models.CharField(
        max_length=255,
        help_text="Location of the issue (Ahmedabad only)"
    )

    # Optional: Latitude and Longitude (for map integration)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        help_text="Latitude (optional, for map integration)"
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        help_text="Longitude (optional, for map integration)"
    )

    # Optional photo as proof
    image = models.ImageField(
        upload_to='report_images/',
        null=True, blank=True,
        help_text="Optional photo of the issue"
    )

    # Attachments (multiple files, e.g., PDFs, more images)
    # Requires a separate model, see below

    # Current status of the report
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the report"
    )

    # Department responsible for this report
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reports',
        help_text="Department assigned to resolve the issue"
    )

    # Authority/official assigned to this report
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_reports',
        help_text="Authority assigned to resolve the issue"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the report was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the report was last updated"
    )

    # Audit fields
    last_updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='updated_reports',
        help_text="Last user who updated the report"
    )

    # Optional: Citizen feedback after resolution
    feedback = models.TextField(
        null=True, blank=True,
        help_text="Citizen feedback after issue is resolved"
    )
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Citizen rating (1-5) after resolution"
    )

    # Optional: For multi-city support
    city = models.CharField(
        max_length=100,
        default="Ahmedabad",
        help_text="City where the issue is reported"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __str__(self):
        return f"{self.get_issue_type_display()} at {self.location} ({self.get_status_display()})"

    def is_resolved(self):
        return self.status == 'resolved'

    def can_give_feedback(self):
        return self.is_resolved() and self.feedback is None

class ReportStatusHistory(models.Model):
    """
    Tracks the status changes of a report for audit and transparency.
    """
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=Report.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Report.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Report Status History"
        verbose_name_plural = "Report Status Histories"

    def __str__(self):
        return f"{self.report} changed from {self.old_status} to {self.new_status} at {self.changed_at}"

class ReportAttachment(models.Model):
    """
    Allows multiple files (images, PDFs, etc.) to be attached to a report.
    """
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='report_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Attachment for {self.report} ({self.file.name})"