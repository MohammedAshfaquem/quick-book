from typing import Optional
from django.db.models import Q
from apps.authentication.models import User
from apps.bookings.constants import BookingFields
from apps.bookings.models import Booking
from apps.core.constants import CommonFields
from apps.events.constants import EventFields


def get_all_bookings(
    user: User | str | None = None,
    status: str | None = None,
    event: str | None = None,
):
    event_vendor_relation = f"{BookingFields.EVENT}__{EventFields.VENDOR}"

    qs = Booking.objects.select_related(
        BookingFields.EVENT,
        event_vendor_relation,
        BookingFields.USER,
    )

    if user:
        if isinstance(user, User):
            qs = qs.filter(user=user)
        else:
            qs = qs.filter(Q(user__email__icontains=user) | Q(user__id__iexact=user))

    if status:
        qs = qs.filter(status__iexact=status)

    if event:
        qs = qs.filter(Q(event__title__icontains=event) | Q(event__id__iexact=event))

    return qs.order_by(CommonFields.UPDATED_AT_DESC)


def get_booking_by_id(booking_id: str) -> Optional[Booking]:
    event_vendor_relation = f"{BookingFields.EVENT}__{EventFields.VENDOR}"

    try:
        return Booking.objects.select_related(
            BookingFields.EVENT,
            event_vendor_relation,
            BookingFields.USER,
        ).get(id=booking_id)
    except Booking.DoesNotExist:
        return None
