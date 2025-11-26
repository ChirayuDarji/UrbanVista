import uuid
from django.conf import settings
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

# ========================================
# Main Travel Experience Model
# ========================================
class TravelExperience(models.Model):
    """
    Main model for user-shared travel experiences, places, or tips.
    """

    EXPERIENCE_TYPE_CHOICES = [
        ('place', 'Place'),
        ('activity', 'Activity'),
        ('story', 'Travel Story'),
        ('tip', 'Travel Tip'),
    ]

    CATEGORY_CHOICES = [
        ('nature', 'Nature'),
        ('adventure', 'Adventure'),
        ('food', 'Food & Drink'),
        ('culture', 'Culture'),
        ('history', 'History'),
        ('shopping', 'Shopping'),
        ('nightlife', 'Nightlife'),
        ('accommodation', 'Accommodation'),
        ('transport', 'Transport'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='travel_experiences',
        db_index=True,
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    experience_type = models.CharField(
        max_length=20,
        choices=EXPERIENCE_TYPE_CHOICES,
        db_index=True,
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
    )

    # Location Data
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Media
    image = models.ImageField(upload_to='travel_experiences/%Y/%m/%d/', null=True, blank=True)

    # Date of visit or experience
    visited_on = models.DateField(null=True, blank=True, help_text="Date of visit or experience")

    # Status & Meta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', db_index=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Engagement
    upvotes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    bookmarks_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['experience_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        verbose_name = 'Travel Experience'
        verbose_name_plural = 'Travel Experiences'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while TravelExperience.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.meta_description:
            self.meta_description = (
                self.description[:157] + '...' if len(self.description) > 157 else self.description
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_experience_type_display()} - {self.title}"

    def get_absolute_url(self):
        return reverse('freecontribution:experience_detail', kwargs={'slug': self.slug})

    @property
    def is_place(self):
        return self.experience_type == 'place'

    @property
    def is_activity(self):
        return self.experience_type == 'activity'

    @property
    def is_story(self):
        return self.experience_type == 'story'

    @property
    def is_tip(self):
        return self.experience_type == 'tip'

    def increment_views(self):
        TravelExperience.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])


# ========================================
# Upvote Model
# ========================================
class ExperienceUpvote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(
        TravelExperience,
        on_delete=models.CASCADE,
        related_name='upvotes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experience_upvotes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['experience', 'user'], name='uq_experience_upvote'),
        ]

    def __str__(self):
        return f"{self.user} upvoted {self.experience.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.experience.upvotes_count = self.experience.upvotes.count()
            self.experience.save(update_fields=['upvotes_count'])

    def delete(self, *args, **kwargs):
        experience = self.experience
        super().delete(*args, **kwargs)
        experience.upvotes_count = experience.upvotes.count()
        experience.save(update_fields=['upvotes_count'])


# ========================================
# Comment Model
# ========================================
class ExperienceComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(
        TravelExperience,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experience_comments',
    )
    comment = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_approved = models.BooleanField(default=True)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['experience', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.experience.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.parent:
            self.experience.comments_count = self.experience.comments.filter(parent=None).count()
            self.experience.save(update_fields=['comments_count'])

    def delete(self, *args, **kwargs):
        experience = self.experience
        super().delete(*args, **kwargs)
        experience.comments_count = experience.comments.filter(parent=None).count()
        experience.save(update_fields=['comments_count'])

    @property
    def is_reply(self):
        return self.parent is not None


# ========================================
# Comment Like Model
# ========================================
class CommentLike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        ExperienceComment,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['comment', 'user'], name='uq_comment_like'),
        ]

    def __str__(self):
        return f"{self.user} liked comment by {self.comment.user}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.comment.likes_count = self.comment.likes.count()
            self.comment.save(update_fields=['likes_count'])

    def delete(self, *args, **kwargs):
        comment = self.comment
        super().delete(*args, **kwargs)
        comment.likes_count = comment.likes.count()
        comment.save(update_fields=['likes_count'])


# ========================================
# Experience Media Model (for multiple images/videos)
# ========================================
class ExperienceMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]
    experience = models.ForeignKey(
        TravelExperience,
        on_delete=models.CASCADE,
        related_name='media_files',
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    file = models.FileField(upload_to='experience_media/%Y/%m/%d/')
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)    
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Media File'
        verbose_name_plural = 'Media Files'

    def __str__(self):
        return f"{self.media_type} for {self.experience.title}"


# ========================================
# Experience Report/Flag Model
# ========================================
class ExperienceReport(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('misleading', 'Misleading Information'),
        ('duplicate', 'Duplicate'),
        ('offensive', 'Offensive'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(
        TravelExperience,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experience_reports',
    )
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_experience_reports',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    action_taken = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['experience', 'reported_by'], name='uq_experience_report'),
        ]
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        return f"Report by {self.reported_by} on {self.experience.title}"


# ========================================
# User Activity Log
# ========================================
class ExperienceActivity(models.Model):
    ACTIVITY_TYPES = [
        ('view', 'View'),
        ('share', 'Share'),
        ('bookmark', 'Bookmark'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(
        TravelExperience,
        on_delete=models.CASCADE,
        related_name='activities',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experience_activities',
        null=True,
        blank=True,
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['experience', 'activity_type']),
        ]
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        user_str = str(self.user) if self.user else 'Anonymous'
        return f"{user_str} - {self.activity_type} - {self.experience.title}"


# ========================================
# Bookmark Model
# ========================================
class ExperienceBookmark(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(
        TravelExperience,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_experiences',
    )
    note = models.TextField(blank=True, help_text="Personal note about this bookmark")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['experience', 'user'], name='uq_experience_bookmark'),
        ]
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'

    def __str__(self):
        return f"{self.user} bookmarked {self.experience.title}"
    