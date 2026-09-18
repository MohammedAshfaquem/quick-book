from django.contrib import admin
from apps.authentication.constants import UserFields
from apps.bookings.constants import BookingFields
from apps.bookings.models import Booking
from apps.core.constants import CommonFields
from apps.events.constants import EventFields


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        CommonFields.ID,
        BookingFields.USER,
        BookingFields.EVENT,
        BookingFields.SEATS,
        BookingFields.TOTAL_PRICE,
        BookingFields.STATUS,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
    list_filter = [BookingFields.STATUS, BookingFields.EVENT]
    search_fields = [
        CommonFields.ID,
        f"{BookingFields.USER}__{UserFields.EMAIL}",
        f"{BookingFields.EVENT}__{EventFields.TITLE}",
    ]
    ordering = [CommonFields.CREATED_AT_DESC]
    readonly_fields = [
        CommonFields.ID,
        BookingFields.TOTAL_PRICE,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
