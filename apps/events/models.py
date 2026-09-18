from django.db import models
from django.utils import timezone

from apps.core.constants import CommonFields, VerboseNames
from apps.core.mixins import BaseModel
from apps.events.constants import ShowStatus
from apps.vendors.models import Vendor


class Event(BaseModel):

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    venue = models.CharField(max_length=255)
    banner_url = models.URLField(blank=True, default="",)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    booking_start_date = models.DateTimeField()
    booking_end_date = models.DateTimeField(null=True, blank=True)
    show_start_date = models.DateTimeField()
    show_end_date = models.DateTimeField()

    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    reserved_seats = models.PositiveIntegerField(default=0)
    min_seats_per_booking = models.PositiveIntegerField(default=1)
    max_seats_per_booking = models.PositiveIntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = VerboseNames.Event.NAME
        verbose_name_plural = VerboseNames.Event.PLURAL
        ordering = [CommonFields.UPDATED_AT_DESC]

    def __str__(self) -> str:
        """Return event title as string representation."""
        return self.title

    @property
    def show_status(self) -> str:
        """
        Calculate current show status based on timezone-aware datetime:
        - EXPIRED: now >= show_end_date
        - RUNNING: show_start_date <= now < show_end_date
        - BOOKING_ENABLED: booking_start_date <= now < min(booking_end_date, show_start_date)
        - UPCOMING: now < booking_start_date or (booking_end_date <= now < show_start_date)
        """
        now = timezone.now()

        # 1. EXPIRED: Show has ended
        if now >= self.show_end_date:
            return ShowStatus.EXPIRED

        # 2. RUNNING: Show is in progress
        if self.show_start_date <= now < self.show_end_date:
            return ShowStatus.RUNNING

        # Effective booking cutoff (booking_end_date or show_start_date)
        booking_cutoff = self.booking_end_date if self.booking_end_date else self.show_start_date

        # 3. BOOKING_ENABLED: Active booking period
        if self.booking_start_date <= now < booking_cutoff and now < self.show_start_date:
            return ShowStatus.BOOKING_ENABLED

        # 4. UPCOMING: Before booking starts OR between booking_end_date and show_start_date
        return ShowStatus.UPCOMING

    @property
    def is_upcoming(self) -> bool:
        """Return True if show is upcoming."""
        return self.show_status == ShowStatus.UPCOMING

    @property
    def is_ongoing(self) -> bool:
        """Return True if show is currently running."""
        return self.show_status == ShowStatus.RUNNING

    @property
    def is_booking_open(self) -> bool:
        """Return True if booking is enabled."""
        return self.show_status == ShowStatus.BOOKING_ENABLED

    @property
    def is_sold_out(self) -> bool:
        """Return True if no seats are available."""
        return self.available_seats == 0

