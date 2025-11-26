from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from allauth.account import views as account_views
from .views import home, about, help_center  # <-- your home view

# Import admin customizations (this applies the customizations to admin.site)
import mysite.admin  # noqa: F401

urlpatterns = [
    # Home
    path("", home, name="home"),
    
    # About Us
    path("about/", about, name="about"),
    
    # Help Center
    path("help/", help_center, name="help_center"),

    # Admin - Changed URL for security (obscurity is not security, but helps)
    # Access admin at /urbansite-admin/ instead of /admin/
    path("urbansite-admin/", admin.site.urls),
    # Redirect old admin URL to new one (optional - can remove in production)
    path("admin/", RedirectView.as_view(url="/urbansite-admin/", permanent=False)),

    # Auth (mount allauth views at clean paths)
    path("login/",  account_views.LoginView.as_view(),  name="account_login"),
    path("signup/", account_views.SignupView.as_view(), name="account_signup"),
    path("password/reset/", account_views.PasswordResetView.as_view(), name="account_reset_password"),

    # Keep provider callbacks and remaining allauth URLs
    path("accounts/", include("allauth.urls")),

    # Optional: redirect default allauth pages to the clean paths
    path("accounts/login/", RedirectView.as_view(pattern_name="account_login", permanent=False)),
    path("accounts/signup/", RedirectView.as_view(pattern_name="account_signup", permanent=False)),
    path("accounts/password/reset/", RedirectView.as_view(pattern_name="account_reset_password", permanent=False)),
    
    
    #other apps urls
    path("free-contribution/", include("FreeContribution.urls", namespace="freecontribution")),    
    path('news/', include(('news.urls', 'news'), namespace='news')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('api/', include('api.urls')),
    path('urbansite/', include('UrbanSite.urls', namespace='urbansite')),  # Added for tests compatibility
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)