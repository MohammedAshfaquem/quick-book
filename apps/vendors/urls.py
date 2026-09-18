from django.urls import path

from apps.vendors.constants import VendorNames, VendorUrls
from apps.vendors.views import (
    VendorCreateView,
    VendorDetailView,
    VendorListView,
    VendorStatusView,
    VendorUpdateView,
)

urlpatterns = [
    path(VendorUrls.CREATE, VendorCreateView.as_view(), name=VendorNames.CREATE),
    path(VendorUrls.UPDATE, VendorUpdateView.as_view(), name=VendorNames.UPDATE),
    path(VendorUrls.DETAIL, VendorDetailView.as_view(), name=VendorNames.DETAIL),
    path(VendorUrls.STATUS, VendorStatusView.as_view(), name=VendorNames.STATUS),
    path(VendorUrls.LIST,   VendorListView.as_view(),   name=VendorNames.LIST),
]
