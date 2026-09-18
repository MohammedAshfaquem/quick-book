from django.urls import path

from apps.events.constants import EventNames, EventUrls
from apps.events.views import (
    EventCreateView,
    EventDetailView,
    EventListView,
    EventStatusView,
    EventUpdateView,
)

urlpatterns = [
    path(EventUrls.CREATE, EventCreateView.as_view(), name=EventNames.CREATE),
    path(EventUrls.UPDATE, EventUpdateView.as_view(), name=EventNames.UPDATE),
    path(EventUrls.DETAIL, EventDetailView.as_view(), name=EventNames.DETAIL),
    path(EventUrls.STATUS, EventStatusView.as_view(), name=EventNames.STATUS),
    path(EventUrls.LIST,   EventListView.as_view(),   name=EventNames.LIST),
]
