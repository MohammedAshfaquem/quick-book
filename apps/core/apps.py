"""
Core app config.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core utilities app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
