from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import ActionType
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.pagination import StandardResultsPagination
from apps.core.permissions import IsStaffUser
from apps.events.constants import EventFields
from apps.events.selectors import get_all_events, get_event_by_id
from apps.events.serializers import (
    EventSerializer,
    EventStatusSerializer,
    EventUpdateSerializer,
)
from apps.events.services import create_event, set_event_status, update_event


class EventListView(APIView):

    permission_classes = [AllowAny]
    serializer_class = EventSerializer

    def get(self, request):
        name        = request.query_params.get(EventFields.FILTER_NAME)
        status      = request.query_params.get(EventFields.FILTER_STATUS)
        show_status = request.query_params.get(EventFields.FILTER_SHOW_STATUS)
        vendor      = request.query_params.get(EventFields.FILTER_VENDOR)

        paginator = StandardResultsPagination()
        events = get_all_events(name=name, status=status, show_status=show_status, vendor=vendor)
        page = paginator.paginate_queryset(events, request)
        serializer = EventSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class EventCreateView(APIView):

    permission_classes = [IsStaffUser]
    serializer_class = EventSerializer

    def post(self, request):
        """Create a new event."""
        serializer = EventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = create_event(serializer.validated_data, action=action)

        if result is None:
            return Response({"message": "Validation successful.", "action": action}, status=status.HTTP_200_OK)

        return Response(
            EventSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class EventDetailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EventSerializer

    def get(self, request, pk):
        """Return a single event's details."""
        event = get_event_by_id(pk)

        if event is None:
            raise QuickBookException(Errors.Event.NOT_FOUND)

        return Response(EventSerializer(event).data)


class EventUpdateView(APIView):
    permission_classes = [IsStaffUser]
    serializer_class = EventUpdateSerializer

    def patch(self, request, pk):
        """Partially update event details."""
        event = get_event_by_id(pk)

        if event is None:
            raise QuickBookException(Errors.Event.NOT_FOUND)

        serializer = EventUpdateSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = update_event(pk, serializer.validated_data, action=action)

        if result is None:
            return Response({"message": "Validation successful.", "action": action}, status=status.HTTP_200_OK)
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)

        return Response(EventSerializer(result).data)


class EventStatusView(APIView):
    permission_classes = [IsStaffUser]
    serializer_class = EventStatusSerializer

    def patch(self, request, pk):
        """Set event is_active status."""
        serializer = EventStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = set_event_status(
            event_id=pk,
            is_active=serializer.validated_data[EventFields.IS_ACTIVE],
            action=action,
        )

        if result is None:
            return Response({"message": "Validation successful.", "action": action}, status=status.HTTP_200_OK)
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)

        return Response(EventSerializer(result).data)

