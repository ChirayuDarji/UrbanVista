from django.contrib import admin
from .models import (
    TravelExperience,
    ExperienceUpvote,
    ExperienceComment,
    CommentLike,
    ExperienceMedia,
    ExperienceReport,
    ExperienceActivity,
    ExperienceBookmark,
)

# Inline for media files
class ExperienceMediaInline(admin.TabularInline):
    model = ExperienceMedia
    extra = 1

# Inline for comments
class ExperienceCommentInline(admin.TabularInline):
    model = ExperienceComment
    extra = 1
    fields = ('user', 'comment', 'created_at', 'is_approved')
    readonly_fields = ('created_at',)

# Main TravelExperience admin
@admin.register(TravelExperience)
class TravelExperienceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'experience_type', 'category', 'country', 'city',
        'status', 'created_at', 'upvotes_count', 'comments_count', 'views_count'
    )
    list_filter = ('experience_type', 'category', 'status', 'country', 'city', 'created_at')
    search_fields = ('title', 'description', 'location', 'country', 'city', 'user__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'upvotes_count', 'comments_count', 'views_count', 'shares_count', 'bookmarks_count')
    inlines = [ExperienceMediaInline, ExperienceCommentInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

# Upvotes admin
@admin.register(ExperienceUpvote)
class ExperienceUpvoteAdmin(admin.ModelAdmin):
    list_display = ('experience', 'user', 'created_at')
    search_fields = ('experience__title', 'user__username')
    list_filter = ('created_at',)

# Comments admin
@admin.register(ExperienceComment)
class ExperienceCommentAdmin(admin.ModelAdmin):
    list_display = ('experience', 'user', 'short_comment', 'is_approved', 'created_at')
    search_fields = ('experience__title', 'user__username', 'comment')
    list_filter = ('is_approved', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')

    def short_comment(self, obj):
        return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
    short_comment.short_description = 'Comment'

# Comment likes admin
@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'created_at')
    search_fields = ('comment__comment', 'user__username')
    list_filter = ('created_at',)

# Media admin
@admin.register(ExperienceMedia)
class ExperienceMediaAdmin(admin.ModelAdmin):
    list_display = ('experience', 'media_type', 'caption', 'order', 'created_at')
    search_fields = ('experience__title', 'caption')
    list_filter = ('media_type', 'created_at')
    ordering = ('experience', 'order')

# Reports admin
@admin.register(ExperienceReport)
class ExperienceReportAdmin(admin.ModelAdmin):
    list_display = ('experience', 'reported_by', 'reason', 'is_reviewed', 'created_at')
    search_fields = ('experience__title', 'reported_by__username', 'description')
    list_filter = ('reason', 'is_reviewed', 'created_at')
    readonly_fields = ('created_at',)

# Activity admin
@admin.register(ExperienceActivity)
class ExperienceActivityAdmin(admin.ModelAdmin):
    list_display = ('experience', 'user', 'activity_type', 'ip_address', 'created_at')
    search_fields = ('experience__title', 'user__username', 'ip_address')
    list_filter = ('activity_type', 'created_at')

# Bookmarks admin
@admin.register(ExperienceBookmark)
class ExperienceBookmarkAdmin(admin.ModelAdmin):
    list_display = ('experience', 'user', 'created_at')
    search_fields = ('experience__title', 'user__username', 'note')
    list_filter = ('created_at',)