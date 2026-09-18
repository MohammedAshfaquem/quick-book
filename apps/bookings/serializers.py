from rest_framework import serializers
from apps.authentication.constants import UserFields
from apps.bookings.constants import BookingFields, BookingStatus
from apps.bookings.models import Booking
from apps.core.constants import CommonFields
from apps.core.messages import Messages
from apps.events.constants import EventFields, ShowStatus
from apps.events.models import Event
from apps.vendors.constants import VendorFields


class BookingSerializer(serializers.ModelSerializer):

    user_email = serializers.CharField(
        source=f"{BookingFields.USER}.{UserFields.EMAIL}",
        read_only=True,
    )
    event_title = serializers.CharField(
        source=f"{BookingFields.EVENT}.{EventFields.TITLE}",
        read_only=True,
    )
    event_start_date = serializers.DateTimeField(
        source=f"{BookingFields.EVENT}.{EventFields.START_DATE}",
        read_only=True,
    )
    vendor_name = serializers.CharField(
        source=f"{BookingFields.EVENT}.{EventFields.VENDOR}.{VendorFields.COMPANY_NAME}",
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = [
            CommonFields.ID,
            BookingFields.USER,
            BookingFields.USER_EMAIL,
            BookingFields.EVENT,
            BookingFields.EVENT_TITLE,
            BookingFields.EVENT_START_DATE,
            BookingFields.VENDOR_NAME,
            BookingFields.SEATS,
            BookingFields.TOTAL_PRICE,
            BookingFields.STATUS,
            CommonFields.CREATED_AT,
            CommonFields.UPDATED_AT,
        ]
        read_only_fields = [
            CommonFields.ID,
            BookingFields.USER,
            BookingFields.USER_EMAIL,
            BookingFields.EVENT_TITLE,
            BookingFields.EVENT_START_DATE,
            BookingFields.VENDOR_NAME,
            BookingFields.TOTAL_PRICE,
            CommonFields.CREATED_AT,
            CommonFields.UPDATED_AT,
        ]


class BookingCreateSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    seats = serializers.IntegerField(default=1, min_value=1)

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError(Messages.Booking.EVENT_NOT_FOUND)

        if not event.is_active:
            raise serializers.ValidationError(Messages.Booking.EVENT_INACTIVE)

        if event.show_status != ShowStatus.BOOKING_ENABLED:
            raise serializers.ValidationError(Messages.Booking.BOOKING_NOT_OPEN)

        return value

    def validate(self, attrs):
        event_id = attrs[BookingFields.EVENT_ID]
        requested_seats = attrs[BookingFields.SEATS]

        try:
            event = Event.objects.get(id=event_id)
            if requested_seats < event.min_seats_per_booking:
                raise serializers.ValidationError(
                    {
                        BookingFields.SEATS: Messages.Booking.MIN_SEATS_NOT_MET.format(
                            min_seats=event.min_seats_per_booking,
                        )
                    }
                )
            if requested_seats > event.max_seats_per_booking:
                raise serializers.ValidationError(
                    {
                        BookingFields.SEATS: Messages.Booking.MAX_LIMIT_REACHED.format(
                            max_seats=event.max_seats_per_booking,
                        )
                    }
                )
            if event.available_seats < requested_seats:
                raise serializers.ValidationError(
                    {
                        BookingFields.SEATS: Messages.Booking.SEATS_UNAVAILABLE.format(
                            available=event.available_seats,
                            requested=requested_seats,
                        )
                    }
                )
        except Event.DoesNotExist:
            pass

        return attrs


class BookingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=BookingStatus.choices)
