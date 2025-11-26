"""
Context processors for Django templates
"""
from django.contrib import admin
from django.urls import reverse, NoReverseMatch


def admin_apps_context(request):
    """Add admin apps list to all admin templates"""
    if not request.path.startswith('/urbansite-admin/') and not request.path.startswith('/admin/'):
        return {}
    
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {}
    
    app_dict = {}
    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label
        if app_label not in app_dict:
            try:
                app_name = admin.site.get_app_label(app_label)
            except:
                app_name = app_label.replace('_', ' ').title()
            app_dict[app_label] = {
                'name': app_name,
                'app_label': app_label,
                'models': [],
            }
        
        if model_admin.has_view_permission(request):
            model_dict = {
                'name': model._meta.verbose_name_plural.title(),
                'object_name': model.__name__,
                'admin_url': None,
                'add_url': None,
            }
            if model_admin.has_view_permission(request):
                try:
                    model_dict['admin_url'] = reverse(f'admin:{app_label}_{model._meta.model_name}_changelist')
                except NoReverseMatch:
                    pass
            if model_admin.has_add_permission(request):
                try:
                    model_dict['add_url'] = reverse(f'admin:{app_label}_{model._meta.model_name}_add')
                except NoReverseMatch:
                    pass
            
            app_dict[app_label]['models'].append(model_dict)
    
    return {
        'admin_app_list': [app for app in app_dict.values() if app['models']]
    }
