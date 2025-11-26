from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """Set a reasonable default Content-Security-Policy.

    Relaxed to allow current inline styles/scripts in templates.
    For production, prefer django-csp with nonces/hashes and remove 'unsafe-inline'.
    """

    def process_response(self, request, response):
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' https:; "
            "style-src 'self' 'unsafe-inline' https:; "
            "connect-src 'self' https:; "
            "font-src 'self' data: https:; "
            "frame-ancestors 'none'"
        )
        response.headers.setdefault('Content-Security-Policy', csp)
        return response


