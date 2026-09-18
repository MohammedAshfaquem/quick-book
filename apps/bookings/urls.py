from django.urls import path
from apps.bookings.constants import BookingNames, BookingUrls
from apps.bookings.views import (
    BookingCleanupView,
    BookingCreateView,
    BookingDetailView,
    BookingListView,
    BookingStatusView,
    BookingUpdateView,
)

urlpatterns = [
    path(BookingUrls.CREATE,  BookingCreateView.as_view(),  name=BookingNames.CREATE),
    path(BookingUrls.UPDATE,  BookingUpdateView.as_view(),  name=BookingNames.UPDATE),
    path(BookingUrls.DETAIL,  BookingDetailView.as_view(),  name=BookingNames.DETAIL),
    path(BookingUrls.STATUS,  BookingStatusView.as_view(),  name=BookingNames.STATUS),
    path(BookingUrls.LIST,    BookingListView.as_view(),    name=BookingNames.LIST),
    path(BookingUrls.CLEANUP, BookingCleanupView.as_view(), name=BookingNames.CLEANUP),
]

