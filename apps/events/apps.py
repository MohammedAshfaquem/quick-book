"""Events app config."""
from django.apps import AppConfig


class EventsConfig(AppConfig):
    """Config for the events app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.events"
    label = "events"
