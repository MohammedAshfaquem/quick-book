"""
Local development settings — extends base.py.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Allow Django debug toolbar or local tools
INSTALLED_APPS += []  # noqa: F405

# Relaxed password validation in dev
AUTH_PASSWORD_VALIDATORS = []
