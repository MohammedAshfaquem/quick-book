"""
Core app rate limiting decorators using django-ratelimit package.
"""

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


def ratelimit_login():
    """Rate limit login requests (5 attempts per minute per IP)."""
    return method_decorator(ratelimit(key="ip", rate="5/m", block=True))


def ratelimit_register():
    """Rate limit account registration requests (10 per minute per IP)."""
    return method_decorator(ratelimit(key="ip", rate="10/m", block=True))


def ratelimit_booking():
    """Rate limit booking creation requests (20 requests per minute per user/IP)."""
    return method_decorator(ratelimit(key="user_or_ip", rate="20/m", block=True))


def ratelimit_sensitive():
    """Rate limit sensitive API operations (30 requests per minute per user/IP)."""
    return method_decorator(ratelimit(key="user_or_ip", rate="30/m", block=True))
