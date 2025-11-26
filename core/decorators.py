from __future__ import annotations

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


def group_required(group_name: str):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise PermissionDenied
            if not user.groups.filter(name=group_name).exists() and not user.is_superuser:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def rate_limit(key_prefix: str, limit: int = 10, window_seconds: int = 60):
    """Simple rate limiter using Django cache.

    Args:
        key_prefix: logical name of the endpoint
        limit: max requests within window
        window_seconds: window size
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            client = request.user.pk if request.user.is_authenticated else request.META.get('REMOTE_ADDR') or 'anon'
            path = iri_to_uri(request.path)
            key = f"rl:{key_prefix}:{client}:{path}"
            try:
                count = cache.get(key, 0)
                if count >= limit:
                    return HttpResponse("Rate limit exceeded. Please try again later.", status=429)
                if count == 0:
                    cache.set(key, 1, timeout=window_seconds)
                else:
                    cache.incr(key)
            except Exception:
                # Fail open on cache errors
                pass
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


