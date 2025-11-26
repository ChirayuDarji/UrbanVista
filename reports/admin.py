# reports/admin.py

from django.contrib import admin
from .models import Report, Department, ReportStatusHistory, ReportAttachment

class ReportAttachmentInline(admin.TabularInline):
    model = ReportAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'uploaded_by')
    can_delete = True

class ReportStatusHistoryInline(admin.TabularInline):
    model = ReportStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'changed_at', 'remarks')
    can_delete = False

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number')
    search_fields = ('name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'issue_type', 'location', 'status', 'department', 'assigned_to',
        'user', 'city', 'created_at', 'image_tag',
    )
    list_filter = (
        'issue_type', 'status', 'department', 'city', 'created_at', 'assigned_to',
    )
    search_fields = (
        'location', 'description', 'user__username', 'assigned_to__username', 'department__name', 'city',
    )
    list_editable = (
        'status', 'assigned_to', 'department',
    )
    readonly_fields = (
        'created_at', 'updated_at', 'image_tag', 'last_updated_by',
    )
    fields = (
        'user', 'issue_type', 'description', 'location', 'latitude', 'longitude',
        'image', 'image_tag', 'status', 'department', 'assigned_to', 'city',
        'created_at', 'updated_at', 'last_updated_by', 'feedback', 'rating',
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [ReportAttachmentInline, ReportStatusHistoryInline]
    actions = ['export_as_csv']

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="80" height="60" style="object-fit:cover;" />'
        return "No Image"
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True
    image_tag.admin_order_field = 'image'

    def save_model(self, request, obj, form, change):
        # Track who last updated the report
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=reports.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Export Selected as CSV"

@admin.register(ReportStatusHistory)
class ReportStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('report', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_by', 'changed_at')
    search_fields = ('report__location', 'report__description', 'changed_by__username')

@admin.register(ReportAttachment)
class ReportAttachmentAdmin(admin.ModelAdmin):
    list_display = ('report', 'file', 'uploaded_at', 'uploaded_by')
    search_fields = ('report__location', 'file')
    readonly_fields = ('uploaded_at', 'uploaded_by')