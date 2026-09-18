"""Dashboard app config."""
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """Config for the custom staff dashboard app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    label = "dashboard"
