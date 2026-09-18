"""
Staff Dashboard URL routes.

Prefixed with /dashboard/ in root urls.py
"""

from django.urls import path

from apps.dashboard.constants import DashboardNames, DashboardUrls
from apps.dashboard.views import (
    BookingCancelView,
    BookingDetailView,
    BookingListView,
    BookingStatusUpdateView,
    DashboardLoginView,
    DashboardLogoutView,
    DashboardOverviewView,
    EventAddView,
    EventDetailView,
    EventEditView,
    EventListView,
    EventToggleStatusView,
    UserAddView,
    UserDetailView,
    UserEditView,
    UserListView,
    UserToggleStaffView,
    VendorAddView,
    VendorDetailView,
    VendorEditView,
    VendorListView,
    VendorToggleStatusView,
)

app_name = "dashboard"

urlpatterns = [
    # Auth
    path(DashboardUrls.LOGIN, DashboardLoginView.as_view(), name=DashboardNames.LOGIN),
    path(DashboardUrls.LOGOUT, DashboardLogoutView.as_view(), name=DashboardNames.LOGOUT),

    # Overview
    path(DashboardUrls.OVERVIEW, DashboardOverviewView.as_view(), name=DashboardNames.OVERVIEW),

    # Vendors
    path(DashboardUrls.VENDOR_LIST, VendorListView.as_view(), name=DashboardNames.VENDOR_LIST),
    path(DashboardUrls.VENDOR_ADD, VendorAddView.as_view(), name=DashboardNames.VENDOR_ADD),
    path(DashboardUrls.VENDOR_DETAIL, VendorDetailView.as_view(), name=DashboardNames.VENDOR_DETAIL),
    path(DashboardUrls.VENDOR_EDIT, VendorEditView.as_view(), name=DashboardNames.VENDOR_EDIT),
    path(DashboardUrls.VENDOR_TOGGLE_STATUS, VendorToggleStatusView.as_view(), name=DashboardNames.VENDOR_TOGGLE_STATUS),

    # Events
    path(DashboardUrls.EVENT_LIST, EventListView.as_view(), name=DashboardNames.EVENT_LIST),
    path(DashboardUrls.EVENT_ADD, EventAddView.as_view(), name=DashboardNames.EVENT_ADD),
    path(DashboardUrls.EVENT_DETAIL, EventDetailView.as_view(), name=DashboardNames.EVENT_DETAIL),
    path(DashboardUrls.EVENT_EDIT, EventEditView.as_view(), name=DashboardNames.EVENT_EDIT),
    path(DashboardUrls.EVENT_TOGGLE_STATUS, EventToggleStatusView.as_view(), name=DashboardNames.EVENT_TOGGLE_STATUS),

    # Bookings
    path(DashboardUrls.BOOKING_LIST, BookingListView.as_view(), name=DashboardNames.BOOKING_LIST),
    path(DashboardUrls.BOOKING_DETAIL, BookingDetailView.as_view(), name=DashboardNames.BOOKING_DETAIL),
    path(DashboardUrls.BOOKING_CANCEL, BookingCancelView.as_view(), name=DashboardNames.BOOKING_CANCEL),
    path(DashboardUrls.BOOKING_STATUS_UPDATE, BookingStatusUpdateView.as_view(), name=DashboardNames.BOOKING_STATUS_UPDATE),

    # Users
    path(DashboardUrls.USER_LIST, UserListView.as_view(), name=DashboardNames.USER_LIST),
    path(DashboardUrls.USER_ADD, UserAddView.as_view(), name=DashboardNames.USER_ADD),
    path(DashboardUrls.USER_DETAIL, UserDetailView.as_view(), name=DashboardNames.USER_DETAIL),
    path(DashboardUrls.USER_EDIT, UserEditView.as_view(), name=DashboardNames.USER_EDIT),
    path(DashboardUrls.USER_TOGGLE_STAFF, UserToggleStaffView.as_view(), name=DashboardNames.USER_TOGGLE_STAFF),
]
