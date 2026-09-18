import uuid
from django.db import models

from apps.authentication.models import User
from apps.bookings.constants import BookingFields, BookingStatus
from apps.core.constants import CommonFields, VerboseNames
from apps.core.mixins import BaseModel
from apps.events.models import Event


class Booking(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name=BookingFields.RELATION_BOOKINGS,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name=BookingFields.RELATION_BOOKINGS,
    )
    seats = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )

    class Meta:
        verbose_name = VerboseNames.Booking.NAME
        verbose_name_plural = VerboseNames.Booking.PLURAL
        ordering = [CommonFields.CREATED_AT_DESC]

    def __str__(self) -> str:
        return f"Booking {self.id} ({self.user.email} - {self.event.title})"
