from django.contrib import admin

from apps.core.constants import CommonFields
from apps.events.constants import EventFields
from apps.events.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        CommonFields.ID,
        EventFields.TITLE,
        EventFields.VENDOR,
        EventFields.VENUE,
        EventFields.START_DATE,
        EventFields.END_DATE,
        EventFields.BOOKING_START_DATE,
        EventFields.BOOKING_END_DATE,
        EventFields.TOTAL_SEATS,
        EventFields.AVAILABLE_SEATS,
        EventFields.MIN_SEATS_PER_BOOKING,
        EventFields.MAX_SEATS_PER_BOOKING,
        EventFields.PRICE,
        EventFields.IS_ACTIVE,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
    list_filter = [EventFields.IS_ACTIVE, EventFields.VENDOR]
    search_fields = [EventFields.TITLE, EventFields.VENUE, "vendor__company_name"]
    ordering = [EventFields.START_DATE]
    readonly_fields = [
        CommonFields.ID,
        EventFields.AVAILABLE_SEATS,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
