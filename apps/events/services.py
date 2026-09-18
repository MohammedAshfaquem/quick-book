from typing import Any
from apps.core.constants import ActionType, CommonFields
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.messages import Messages
from apps.events.constants import EventFields, ShowStatus
from apps.events.models import Event
from apps.events.selectors import get_event_by_id


def check_event_action_warning(
    event: Event,
    is_deactivating: bool = False,
    validated_data: dict | None = None,
) -> tuple[bool, str]:
    has_warning = False
    warning_msg = ""
    status = event.show_status
    booked_seats = event.total_seats - event.available_seats

    if is_deactivating:
        if status == ShowStatus.RUNNING:
            has_warning = True
            warning_msg = Messages.Event.WARN_DEACTIVATE_RUNNING.format(title=event.title)
        elif status == ShowStatus.BOOKING_ENABLED or booked_seats > 0:
            has_warning = True
            warning_msg = Messages.Event.WARN_DEACTIVATE_BOOKED.format(title=event.title, count=booked_seats)
        elif status == ShowStatus.EXPIRED:
            has_warning = False
            warning_msg = ""
    else:  # Update / Edit event details
        if status == ShowStatus.RUNNING:
            has_warning = True
            warning_msg = Messages.Event.WARN_EDIT_RUNNING.format(title=event.title)
        elif status == ShowStatus.BOOKING_ENABLED and booked_seats > 0:
            has_warning = True
            warning_msg = Messages.Event.WARN_EDIT_BOOKING_ENABLED.format(title=event.title, count=booked_seats)
        elif status == ShowStatus.EXPIRED:
            has_warning = True
            warning_msg = Messages.Event.WARN_EDIT_EXPIRED.format(title=event.title)

        # Extra check if reducing total_seats below currently booked count
        if validated_data and EventFields.TOTAL_SEATS in validated_data:
            new_total = validated_data[EventFields.TOTAL_SEATS]
            if new_total < booked_seats:
                has_warning = True
                seat_msg = Messages.Event.WARN_SEATS_REDUCED.format(new_total=new_total, count=booked_seats)
                warning_msg = f"{warning_msg} {seat_msg}".strip()

    return has_warning, warning_msg


def create_event(
    validated_data: dict,
    action: str = ActionType.CONFIRM,
) -> Event | dict[str, Any]:
    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Event.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }

    elif action == ActionType.CONFIRM:
        total_seats = validated_data[EventFields.TOTAL_SEATS]
        return Event.objects.create(
            **validated_data,
            available_seats=total_seats,
        )

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)


def update_event(
    event_id: str,
    validated_data: dict,
    action: str = ActionType.CONFIRM,
) -> Event | dict[str, Any]:
    event = get_event_by_id(event_id)

    if event is None:
        raise QuickBookException(Errors.Event.NOT_FOUND)

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Event.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }

    elif action == ActionType.WARNING:
        has_warning, warning_msg = check_event_action_warning(
            event=event,
            is_deactivating=False,
            validated_data=validated_data,
        )
        return {
            "has_warning": has_warning,
            "warning_message": warning_msg,
            "action": ActionType.WARNING,
        }

    elif action == ActionType.CONFIRM:
        for field, value in validated_data.items():
            setattr(event, field, value)

        update_fields = list(validated_data.keys()) + [CommonFields.UPDATED_AT]
        event.save(update_fields=update_fields)
        return event

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)


def set_event_status(
    event_id: str,
    is_active: bool,
    action: str = ActionType.CONFIRM,
) -> Event | dict[str, Any]:
    event = get_event_by_id(event_id)

    if event is None:
        raise QuickBookException(Errors.Event.NOT_FOUND)

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Event.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }

    elif action == ActionType.WARNING:
        has_warning, warning_msg = (False, "")
        if not is_active:
            has_warning, warning_msg = check_event_action_warning(
                event=event,
                is_deactivating=True,
            )

        return {
            "has_warning": has_warning,
            "warning_message": warning_msg,
            "action": ActionType.WARNING,
        }

    elif action == ActionType.CONFIRM:
        event.is_active = is_active
        event.save(update_fields=[EventFields.IS_ACTIVE, CommonFields.UPDATED_AT])
        return event

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)



