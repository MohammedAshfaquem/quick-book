from django.db import models


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class StatusMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampMixin, StatusMixin, models.Model):
    class Meta:
        abstract = True
