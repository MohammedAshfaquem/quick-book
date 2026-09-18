from datetime import timedelta
from typing import Any
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.authentication.models import User
from apps.bookings.constants import BookingFields, BookingStatus
from apps.bookings.models import Booking
from apps.bookings.selectors import get_booking_by_id
from apps.core.constants import ActionType, CommonFields
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.messages import Messages
from apps.events.constants import EventFields
from apps.events.models import Event


def create_booking(
    user: User,
    event_id: str,
    seats: int = 1,
    action: str = ActionType.CONFIRM,
) -> Booking | dict[str, Any]:

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise QuickBookException(Errors.Event.NOT_FOUND)

    if not event.is_active:
        raise QuickBookException(Errors.Event.INACTIVE)

    if not event.is_booking_open:
        raise QuickBookException(Errors.Booking.BOOKING_CLOSED)

    if seats < event.min_seats_per_booking:
        raise QuickBookException(
            Errors.Booking.MIN_SEATS_NOT_MET,
            message=Messages.Booking.MIN_SEATS_NOT_MET.format(min_seats=event.min_seats_per_booking),
        )

    if seats > event.max_seats_per_booking:
        raise QuickBookException(
            Errors.Booking.MAX_SEATS_EXCEEDED,
            message=Messages.Booking.MAX_LIMIT_REACHED.format(max_seats=event.max_seats_per_booking),
        )

    if event.available_seats < seats:
        raise QuickBookException(
            Errors.Booking.NOT_ENOUGH_SEATS,
            message=Messages.Booking.SEATS_UNAVAILABLE.format(available=event.available_seats, requested=seats),
        )

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Booking.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
            "total_price": str(event.price * seats),
        }

    elif action == ActionType.CONFIRM:
        with transaction.atomic():
            event_locked = Event.objects.select_for_update().get(id=event.id)
            total_price = event_locked.price * seats

            if not event_locked.is_active:
                raise QuickBookException(Errors.Event.INACTIVE)

            if not event_locked.is_booking_open:
                raise QuickBookException(Errors.Booking.BOOKING_CLOSED)

            if event_locked.available_seats < seats:
                raise QuickBookException(
                    Errors.Booking.NOT_ENOUGH_SEATS,
                    message=Messages.Booking.SEATS_UNAVAILABLE.format(available=event_locked.available_seats, requested=seats),
                )

            event_locked.available_seats -= seats
            event_locked.reserved_seats += seats
            event_locked.save(
                update_fields=[EventFields.AVAILABLE_SEATS, EventFields.RESERVED_SEATS, CommonFields.UPDATED_AT]
            )

            booking = Booking.objects.create(
                user=user,
                event=event_locked,
                seats=seats,
                total_price=total_price,
                status=BookingStatus.PENDING,
            )

        return booking

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)


def update_booking_status(
    booking_id: str,
    new_status: str,
    requesting_user: User,
    action: str = ActionType.CONFIRM,
) -> Booking | dict[str, Any]:
    booking = get_booking_by_id(booking_id)

    if booking is None:
        raise QuickBookException(Errors.Booking.NOT_FOUND)

    # When Payment Gateway is enabled, status cannot be manually mutated via API
    if getattr(settings, "ENABLE_PAYMENT_GATEWAY", False):
        raise QuickBookException(
            Errors.Auth.PERMISSION_DENIED,
            message=Messages.Booking.PAYMENT_GATEWAY_ENABLED,
        )

    # Non-staff users can only manage their own bookings
    if not requesting_user.is_staff and booking.user != requesting_user:
        raise QuickBookException(Errors.Auth.PERMISSION_DENIED)

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Booking.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }


    elif action == ActionType.CONFIRM:
        with transaction.atomic():
            booking_locked = Booking.objects.select_for_update().get(id=booking_id)
            old_status = booking_locked.status

            if old_status == new_status:
                return booking_locked
            event_locked = Event.objects.select_for_update().get(id=booking_locked.event.id)

            # 1. PENDING -> CONFIRMED
            # Seats were already deducted from available_seats upon selection (PENDING creation).
            # We now release from reserved_seats.
            if old_status == BookingStatus.PENDING and new_status == BookingStatus.CONFIRMED:
                event_locked.reserved_seats = max(0, event_locked.reserved_seats - booking_locked.seats)
                event_locked.save(
                    update_fields=[EventFields.RESERVED_SEATS, CommonFields.UPDATED_AT]
                )

            # 2. PENDING -> CANCELLED or FAILED
            # User cancelled or payment failed while pending: restore available_seats, deduct reserved_seats.
            elif old_status == BookingStatus.PENDING and new_status in (BookingStatus.CANCELLED, BookingStatus.FAILED):
                event_locked.available_seats += booking_locked.seats
                event_locked.reserved_seats = max(0, event_locked.reserved_seats - booking_locked.seats)
                event_locked.save(
                    update_fields=[EventFields.AVAILABLE_SEATS, EventFields.RESERVED_SEATS, CommonFields.UPDATED_AT]
                )

            # 3. CONFIRMED -> CANCELLED or FAILED
            # Booking was confirmed previously, now cancelled: restore available_seats.
            elif old_status == BookingStatus.CONFIRMED and new_status in (BookingStatus.CANCELLED, BookingStatus.FAILED):
                event_locked.available_seats += booking_locked.seats
                event_locked.save(
                    update_fields=[EventFields.AVAILABLE_SEATS, CommonFields.UPDATED_AT]
                )

            # 4. CANCELLED or FAILED -> CONFIRMED
            # Re-confirming a cancelled booking: deduct from available_seats if enough seats are left.
            elif old_status in (BookingStatus.CANCELLED, BookingStatus.FAILED) and new_status == BookingStatus.CONFIRMED:
                if event_locked.available_seats < booking_locked.seats:
                    raise QuickBookException(
                        Errors.Booking.NOT_ENOUGH_SEATS,
                        message=Messages.Booking.SEATS_UNAVAILABLE.format(
                            available=event_locked.available_seats, requested=booking_locked.seats
                        ),
                    )
                event_locked.available_seats -= booking_locked.seats
                event_locked.save(
                    update_fields=[EventFields.AVAILABLE_SEATS, CommonFields.UPDATED_AT]
                )

            booking_locked.status = new_status
            booking_locked.save(update_fields=[BookingFields.STATUS, CommonFields.UPDATED_AT])

        return booking_locked

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)


def cleanup_expired_pending_bookings() -> int:
    hold_minutes = getattr(settings, "BOOKING_TIME_MINUTES", 15)
    cutoff_time = timezone.now() - timedelta(minutes=hold_minutes)

    stale_bookings = Booking.objects.filter(
        status=BookingStatus.PENDING,
        created_at__lte=cutoff_time,
    )

    cleaned_count = 0

    for booking in stale_bookings:
        with transaction.atomic():
            try:
                booking_locked = Booking.objects.select_for_update().get(
                    id=booking.id,
                    status=BookingStatus.PENDING,
                )
            except Booking.DoesNotExist:
                continue

            event_locked = Event.objects.select_for_update().get(id=booking_locked.event.id)

            # Revert reserved ticket count back to available_seats
            event_locked.available_seats += booking_locked.seats
            event_locked.reserved_seats = max(0, event_locked.reserved_seats - booking_locked.seats)
            event_locked.save(
                update_fields=[EventFields.AVAILABLE_SEATS, EventFields.RESERVED_SEATS, CommonFields.UPDATED_AT]
            )

            # Update booking status to FAILED
            booking_locked.status = BookingStatus.FAILED
            booking_locked.save(update_fields=[BookingFields.STATUS, CommonFields.UPDATED_AT])
            cleaned_count += 1

    return cleaned_count




