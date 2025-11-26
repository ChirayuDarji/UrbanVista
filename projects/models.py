# projects/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()

class ProjectCategory(models.Model):
    """Categories for city projects (e.g., Infrastructure, Parks, Roads, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class (e.g., 'fas fa-road')")
    
    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CityProject(models.Model):
    """City infrastructure and development projects"""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, help_text="Brief summary for cards/listings")
    
    # Category and Status
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, related_name='projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Location
    location = models.CharField(max_length=255, help_text="Area/ward where project is located")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    ward = models.CharField(max_length=100, blank=True, help_text="Ward number or name")
    
    # Financial Information
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Budget in INR")
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Actual cost if completed")
    
    # Timeline
    start_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    
    # Responsible Department/Authority
    department = models.ForeignKey(
        'reports.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Department responsible for this project"
    )
    project_manager = models.CharField(max_length=200, blank=True, help_text="Name of project manager or authority")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Media
    featured_image = models.ImageField(upload_to='projects/%Y/%m/', null=True, blank=True)
    
    # Additional Details
    benefits = models.TextField(blank=True, help_text="Benefits to citizens/community")
    challenges = models.TextField(blank=True, help_text="Challenges or issues faced")
    progress_percentage = models.PositiveSmallIntegerField(default=0, help_text="Progress percentage (0-100)")
    
    # Public Engagement
    is_public = models.BooleanField(default=True, help_text="Whether project is visible to public")
    allow_comments = models.BooleanField(default=True, help_text="Allow public comments")
    views_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_projects')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]
        verbose_name = "City Project"
        verbose_name_plural = "City Projects"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while CityProject.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'slug': self.slug})
    
    def is_completed(self):
        return self.status == 'completed'
    
    def is_in_progress(self):
        return self.status == 'in_progress'
    
    def days_remaining(self):
        """Calculate days remaining until expected completion"""
        if self.expected_completion_date and self.status in ['in_progress', 'approved']:
            from django.utils import timezone
            from datetime import date
            today = date.today()
            if self.expected_completion_date > today:
                return (self.expected_completion_date - today).days
        return None


class ProjectUpdate(models.Model):
    """Updates/Progress reports for projects"""
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    content = models.TextField()
    progress_percentage = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Update progress if changed")
    image = models.ImageField(upload_to='projects/updates/%Y/%m/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Project Update"
        verbose_name_plural = "Project Updates"
    
    def __str__(self):
        return f"Update for {self.project.title} - {self.created_at.strftime('%Y-%m-%d')}"


class ProjectDocument(models.Model):
    """Documents related to projects (PDFs, images, etc.)"""
    project = models.ForeignKey(CityProject, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='projects/documents/%Y/%m/')
    file_type = models.CharField(max_length=50, blank=True, help_text="e.g., PDF, Image, Plan")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Project Document"
        verbose_name_plural = "Project Documents"
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"

