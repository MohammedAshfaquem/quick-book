from django.utils import timezone
from rest_framework import serializers

from apps.core.messages import Messages
from apps.events.constants import EventFields
from apps.events.models import Event


def validate_event_dates(attrs: dict, instance: Event | None = None) -> dict:
    now = timezone.now()

    # Get field values from attrs or fallback to instance if updating
    start_date = attrs.get(EventFields.START_DATE, getattr(instance, EventFields.START_DATE, None))
    end_date = attrs.get(EventFields.END_DATE, getattr(instance, EventFields.END_DATE, None))
    booking_start = attrs.get(EventFields.BOOKING_START_DATE, getattr(instance, EventFields.BOOKING_START_DATE, None))
    booking_end = attrs.get(EventFields.BOOKING_END_DATE, getattr(instance, EventFields.BOOKING_END_DATE, None))
    show_start = attrs.get(EventFields.SHOW_START_DATE, getattr(instance, EventFields.SHOW_START_DATE, None))
    show_end = attrs.get(EventFields.SHOW_END_DATE, getattr(instance, EventFields.SHOW_END_DATE, None))

    # 1. Creation-time check: start_date in future
    if instance is None and start_date and start_date <= now:
        raise serializers.ValidationError({EventFields.START_DATE: Messages.Event.START_DATE_IN_FUTURE})

    # 2. Event period: start_date < end_date
    if start_date and end_date and start_date >= end_date:
        raise serializers.ValidationError({EventFields.END_DATE: Messages.Event.END_DATE_AFTER_START})

    # 3. Booking period within Event period
    if start_date and booking_start and booking_start < start_date:
        raise serializers.ValidationError({EventFields.BOOKING_START_DATE: Messages.Event.BOOKING_START_BEFORE_EVENT_START})

    if booking_end:
        if booking_start and booking_end <= booking_start:
            raise serializers.ValidationError({EventFields.BOOKING_END_DATE: Messages.Event.BOOKING_END_AFTER_BOOKING_START})
        if end_date and booking_end > end_date:
            raise serializers.ValidationError({EventFields.BOOKING_END_DATE: Messages.Event.BOOKING_END_AFTER_EVENT_END})

    # 4. Show period within Event period
    if start_date and show_start and show_start < start_date:
        raise serializers.ValidationError({EventFields.SHOW_START_DATE: Messages.Event.SHOW_START_BEFORE_EVENT_START})

    if show_start and show_end and show_end <= show_start:
        raise serializers.ValidationError({EventFields.SHOW_END_DATE: Messages.Event.SHOW_END_AFTER_SHOW_START})

    if end_date and show_end and show_end > end_date:
        raise serializers.ValidationError({EventFields.SHOW_END_DATE: Messages.Event.SHOW_END_AFTER_EVENT_END})

    # 5. Booking vs Show relationship
    if booking_start and show_start and booking_start > show_start:
        raise serializers.ValidationError({EventFields.BOOKING_START_DATE: Messages.Event.BOOKING_START_AFTER_SHOW_START})

    if booking_end and show_start and booking_end > show_start:
        raise serializers.ValidationError({EventFields.BOOKING_END_DATE: Messages.Event.BOOKING_END_AFTER_SHOW_START})

    # 6. Venue schedule conflict check (overlapping active events at the same venue)
    venue = attrs.get(EventFields.VENUE, getattr(instance, EventFields.VENUE, None))
    if venue and start_date and end_date:
        overlapping_qs = Event.objects.filter(
            venue__iexact=venue.strip(),
            is_active=True,
            start_date__lt=end_date,
            end_date__gt=start_date,
        )

        if instance:
            overlapping_qs = overlapping_qs.exclude(pk=instance.pk)

        if overlapping_qs.exists():
            conflict = overlapping_qs.first()
            msg = Messages.Event.VENUE_SCHEDULE_CONFLICT.format(
                venue=venue,
                start=conflict.start_date.strftime("%b %d, %Y %H:%M"),
                end=conflict.end_date.strftime("%b %d, %Y %H:%M"),
            )
            raise serializers.ValidationError({EventFields.VENUE: msg})

    # 7. Seat limits validation
    min_seats = attrs.get(EventFields.MIN_SEATS_PER_BOOKING, getattr(instance, EventFields.MIN_SEATS_PER_BOOKING, 1))
    max_seats = attrs.get(EventFields.MAX_SEATS_PER_BOOKING, getattr(instance, EventFields.MAX_SEATS_PER_BOOKING, 10))
    total_seats = attrs.get(EventFields.TOTAL_SEATS, getattr(instance, EventFields.TOTAL_SEATS, None))

    if min_seats is not None and min_seats < 1:
        raise serializers.ValidationError({EventFields.MIN_SEATS_PER_BOOKING: Messages.Event.MIN_SEATS_AT_LEAST_ONE})

    if min_seats is not None and max_seats is not None and max_seats < min_seats:
        raise serializers.ValidationError({EventFields.MAX_SEATS_PER_BOOKING: Messages.Event.MAX_SEATS_GE_MIN_SEATS})

    if total_seats is not None and max_seats is not None and max_seats > total_seats:
        raise serializers.ValidationError({EventFields.MAX_SEATS_PER_BOOKING: Messages.Event.MAX_SEATS_LE_TOTAL_SEATS})

    return attrs


class EventSerializer(serializers.ModelSerializer):
    """Full serializer for reading and creating event data."""

    vendor_name = serializers.CharField(source="vendor.company_name", read_only=True)
    show_status = serializers.CharField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_booking_open = serializers.BooleanField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "vendor",
            "vendor_name",
            "title",
            "description",
            "venue",
            "banner_url",
            "start_date",
            "end_date",
            "booking_start_date",
            "booking_end_date",
            "show_start_date",
            "show_end_date",
            "show_status",
            "total_seats",
            "available_seats",
            "reserved_seats",
            "min_seats_per_booking",
            "max_seats_per_booking",
            "price",
            "is_active",
            "is_upcoming",
            "is_ongoing",
            "is_booking_open",
            "is_sold_out",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "show_status",
            "available_seats",
            "reserved_seats",
            "is_upcoming",
            "is_ongoing",
            "is_booking_open",
            "is_sold_out",
            "created_at",
            "updated_at",
        ]

    def validate_vendor(self, value):
        """Ensure the vendor is active."""
        if not value.is_active:
            raise serializers.ValidationError(Messages.Event.INACTIVE_VENDOR)
        return value

    def validate_total_seats(self, value):
        """Ensure at least 1 seat."""
        if value < 1:
            raise serializers.ValidationError(Messages.Event.SEATS_MINIMUM)
        return value

    def validate(self, attrs):
        """Cross-field validations for event and booking dates."""
        return validate_event_dates(attrs, self.instance)


class EventUpdateSerializer(serializers.ModelSerializer):
    """Partial update serializer for events — all fields optional."""

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "venue",
            "banner_url",
            "start_date",
            "end_date",
            "booking_start_date",
            "booking_end_date",
            "show_start_date",
            "show_end_date",
            "min_seats_per_booking",
            "max_seats_per_booking",
            "price",
        ]

    def validate(self, attrs):
        """Cross-field validation when updating dates."""
        return validate_event_dates(attrs, self.instance)



class EventStatusSerializer(serializers.Serializer):
    """Serializer for toggling event active/inactive status."""

    is_active = serializers.BooleanField()
