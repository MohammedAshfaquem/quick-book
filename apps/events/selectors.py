from typing import Optional
from django.db.models import Q
from django.utils import timezone
from apps.core.constants import CommonFields, ModuleNames, StatusChoices
from apps.events.constants import EventFields, ShowStatus
from apps.events.models import Event


def get_all_events(
    name: str | None = None,
    status: str | None = None,
    show_status: str | None = None,
    vendor: str | None = None,
):
    now = timezone.now()
    qs = Event.objects.select_related(ModuleNames.VENDOR)

    if name:
        qs = qs.filter(title__icontains=name)

    if status == StatusChoices.ACTIVE:
        qs = qs.filter(is_active=True)
    elif status == StatusChoices.INACTIVE:
        qs = qs.filter(is_active=False)

    if show_status == ShowStatus.EXPIRED:
        # now >= show_end_date
        qs = qs.filter(show_end_date__lte=now)

    elif show_status == ShowStatus.RUNNING:
        # show_start_date <= now < show_end_date
        qs = qs.filter(show_start_date__lte=now, show_end_date__gt=now)

    elif show_status == ShowStatus.BOOKING_ENABLED:
        # booking_start_date <= now < show_start_date
        # AND now < booking_end_date (if set) OR booking_end_date is null
        qs = qs.filter(
            booking_start_date__lte=now,
            show_start_date__gt=now,
        ).filter(
            Q(booking_end_date__isnull=True) | Q(booking_end_date__gt=now)
        )

    elif show_status == ShowStatus.UPCOMING:
        # now < booking_start_date
        qs = qs.filter(booking_start_date__gt=now)

    if vendor:
        qs = qs.filter(vendor__company_name__icontains=vendor)

    return qs.order_by(CommonFields.UPDATED_AT_DESC)






def get_event_by_id(event_id: str) -> Optional[Event]:
    try:
        return Event.objects.select_related(ModuleNames.VENDOR).get(id=event_id)
    except Event.DoesNotExist:
        return None


def get_upcoming_events():
    return Event.objects.filter(
        is_active=True,
        start_date__gt=timezone.now(),
    ).select_related(ModuleNames.VENDOR).order_by(EventFields.START_DATE)


