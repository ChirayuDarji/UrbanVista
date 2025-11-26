# mysite/settings.py
"""
Django settings for mysite project with security best practices.
"""
from pathlib import Path
import os
from django.urls import reverse_lazy
from django.core.exceptions import ImproperlyConfigured

# Try to load dotenv for .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, continue without it
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS - Critical for production
# ============================================================================

# SECRET_KEY: Move to environment variable for security
def get_secret_key():
    """Get SECRET_KEY from environment or raise error in production."""
    secret_key = os.environ.get("DJANGO_SECRET_KEY")
    if not secret_key:
        # In production, this should be set
        if os.environ.get("ENVIRONMENT") == "production":
            raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in environment variables")
        # Development fallback (NEVER use in production)
        secret_key = "dev-secret-key-change-me-in-production"
    return secret_key

SECRET_KEY = get_secret_key()

# DEBUG: Disable in production to prevent information leakage
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

# ALLOWED_HOSTS: Restrict which hosts can serve the site
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ============================================================================
# HTTPS & SSL SECURITY
# ============================================================================

# Force HTTPS in production (set SECURE_SSL_REDIRECT=True in production)
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "False").lower() == "true"

# HTTP Strict Transport Security (HSTS) - Only enable in production with HTTPS
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False").lower() == "true"
SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "False").lower() == "true"

# Secure cookies - Only send over HTTPS
SECURE_SSL_REDIRECT = SECURE_SSL_REDIRECT if not DEBUG else False
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT  # Only send session cookies over HTTPS
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT    # Only send CSRF cookies over HTTPS

# ============================================================================
# XSS & CLICKJACKING PROTECTION
# ============================================================================

# XSS Protection: Enable browser XSS filtering
SECURE_BROWSER_XSS_FILTER = True

# Content Type Sniffing Protection: Prevent MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Clickjacking Protection: Prevent page from being embedded in iframe
X_FRAME_OPTIONS = 'DENY'

# ============================================================================
# INSTALLED APPS
# ============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Required by django-allauth
    "django.contrib.sites",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # other apps...
    "core",
    "FreeContribution",
    "news",
    "reports",
    "projects",
    "UrbanSite",  # Added for tests compatibility
]

SITE_ID = 1

# ============================================================================
# MIDDLEWARE
# ============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Security headers
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Clickjacking protection
    "core.security_middleware.ContentSecurityPolicyMiddleware",
]

# ============================================================================
# AUTHENTICATION
# ============================================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ============================================================================
# URL CONFIGURATION
# ============================================================================

ROOT_URLCONF = "mysite.urls"
WSGI_APPLICATION = "mysite.wsgi.application"

# ============================================================================
# TEMPLATES
# ============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mysite.context.admin_apps_context",
            ],
        },
    },
]

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database configuration - supports both SQLite (dev) and PostgreSQL (production)
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DATABASE_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.environ.get("DATABASE_USER", ""),
        "PASSWORD": os.environ.get("DATABASE_PASSWORD", ""),
        "HOST": os.environ.get("DATABASE_HOST", ""),
        "PORT": os.environ.get("DATABASE_PORT", ""),
    }
}

# ============================================================================
# PASSWORD VALIDATION - Strong password requirements
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "email"),
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,  # Increased from default 8
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC & MEDIA FILES
# ============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Maximum upload size: 5MB (enforced in forms)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================================
# REDIRECTS
# ============================================================================

LOGIN_URL = reverse_lazy("account_login")
LOGIN_REDIRECT_URL = "/"
ACCOUNT_AUTHENTICATED_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# ============================================================================
# ALLAUTH CONFIGURATION
# ============================================================================

ACCOUNT_SIGNUP_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION = os.environ.get("ACCOUNT_EMAIL_VERIFICATION", "none")  # Change to "mandatory" in production
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_USERNAME_GENERATOR = "allauth.account.utils.generate_unique_username"
ACCOUNT_LOGOUT_ON_GET = True

# Social account behavior
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True

# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

# Email backend - supports both file-based (dev) and SMTP (production)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "tmp" / "emails"
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@example.local")
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@yourdomain.com")

# ============================================================================
# GOOGLE OAUTH CONFIGURATION
# ============================================================================

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"prompt": "select_account"},
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        },
    }
}

# ============================================================================
# CACHING CONFIGURATION (for rate limiting)
# ============================================================================

REDIS_URL = os.environ.get("REDIS_URL", "")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "TIMEOUT": 300,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
            "TIMEOUT": 300,  # 5 minutes default
        }
    }

# Cookie security
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "security_file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "security.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG" if DEBUG else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "UrbanSite": {
            "handlers": ["file", "security_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================================================
# SECURITY: Additional Headers
# ============================================================================

# Referrer Policy: Control how much referrer information is sent
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Permissions Policy: Control browser features
PERMISSIONS_POLICY = {
    "geolocation": [],
    "camera": [],
    "microphone": [],
}

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0"))
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"  # for tests

