"""
Custom Admin Configuration for UrbanVista
Modern, attractive admin interface with custom branding
"""
from django.contrib import admin

# Customize the default admin site
admin.site.site_header = "UrbanVista Administration"
admin.site.site_title = "UrbanVista Admin"
admin.site.index_title = "Welcome to UrbanVista Administration"
admin.site.site_url = "/"
admin.site.empty_value_display = "-"

