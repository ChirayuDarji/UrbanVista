# projects/admin.py

from django.contrib import admin
from .models import ProjectCategory, CityProject, ProjectUpdate, ProjectDocument


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 1
    fields = ['title', 'content', 'progress_percentage', 'image', 'created_at']


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 1
    fields = ['title', 'file', 'file_type', 'uploaded_at']


@admin.register(CityProject)
class CityProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'priority', 'location', 'progress_percentage', 'is_public', 'created_at']
    list_filter = ['status', 'priority', 'category', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'location', 'ward']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    inlines = [ProjectUpdateInline, ProjectDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category', 'featured_image')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'progress_percentage')
        }),
        ('Location', {
            'fields': ('location', 'ward', 'latitude', 'longitude')
        }),
        ('Timeline', {
            'fields': ('start_date', 'expected_completion_date', 'actual_completion_date')
        }),
        ('Financial', {
            'fields': ('estimated_budget', 'actual_cost')
        }),
        ('Responsibility', {
            'fields': ('department', 'project_manager', 'contact_email', 'contact_phone')
        }),
        ('Additional Details', {
            'fields': ('benefits', 'challenges')
        }),
        ('Settings', {
            'fields': ('is_public', 'allow_comments')
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'progress_percentage', 'created_by', 'created_at']
    list_filter = ['created_at', 'project']
    search_fields = ['title', 'content', 'project__title']


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'file_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['title', 'project__title']

