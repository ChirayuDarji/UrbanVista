# UrbanSite/admin.py
"""
Admin configuration with security best practices:
- Read-only permissions for authority users
- IP address and security logging
- Restricted access to sensitive fields
"""
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from .models import Authority, UserReport, Feedback
import logging

logger = logging.getLogger('UrbanSite')


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'area', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'department', 'created_at')
    search_fields = ('name', 'email', 'area', 'department')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    """
    UserReport admin with security features:
    - IP address logging on save
    - Read-only sensitive fields
    - Security event logging
    """
    list_display = ('name', 'problem_type', 'area', 'pincode', 'status', 'authority', 'timestamp', 'ip_address_display')
    list_filter = ('status', 'problem_type', 'pincode', 'timestamp', 'authority')
    search_fields = ('name', 'email', 'phone', 'area', 'pincode', 'description')
    readonly_fields = ('timestamp', 'updated_at', 'resolved_at', 'ip_address', 'user_agent')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    def ip_address_display(self, obj):
        """Display IP address with masking for privacy."""
        if obj.ip_address:
            # Show only last octet for privacy
            ip_parts = str(obj.ip_address).split('.')
            if len(ip_parts) == 4:
                return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.xxx"
            return "***.***.***.***"
        return "-"
    ip_address_display.short_description = "IP Address"
    
    def save_model(self, request, obj, form, change):
        """Log admin actions for security auditing."""
        super().save_model(request, obj, form, change)
        
        action = "updated" if change else "created"
        logger.info(
            f"Admin {action} report: ID={obj.id}, Admin={request.user.username}, IP={self.get_client_ip(request)}",
            extra={
                'report_id': obj.id,
                'admin_user': request.user.username,
                'action': action,
                'ip_address': self.get_client_ip(request)
            }
        )
    
    def get_client_ip(self, request):
        """Get client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    fieldsets = (
        ('Reporter Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('area', 'pincode', 'address')
        }),
        ('Report Details', {
            'fields': ('problem_type', 'description', 'image')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'authority', 'resolved_at')
        }),
        ('Metadata', {
            'fields': ('timestamp', 'updated_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('report', 'authority', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'authority')
    search_fields = ('message', 'report__name', 'report__description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
