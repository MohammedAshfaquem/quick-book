from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.bookings.constants import BookingFields
from apps.bookings.selectors import (
    get_all_bookings,
    get_booking_by_id,
)
from apps.bookings.serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    BookingStatusSerializer,
)
from apps.bookings.services import (
    cleanup_expired_pending_bookings,
    create_booking,
    update_booking_status,
)
from apps.core.constants import ActionType
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.messages import Messages
from apps.core.pagination import StandardResultsPagination
from apps.core.throttling import ratelimit_booking, ratelimit_sensitive


class BookingCreateView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = BookingCreateSerializer

    @ratelimit_booking()
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = create_booking(
            user=request.user,
            event_id=str(serializer.validated_data["event_id"]),
            seats=serializer.validated_data["seats"],
            action=action,
        )

        if result is None:
            return Response({"message": Messages.Validation.SUCCESS, "action": action}, status=status.HTTP_200_OK)

        return Response(
            BookingSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class BookingUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def patch(self, request, pk):
        booking = get_booking_by_id(pk)

        if booking is None:
            raise QuickBookException(Errors.Booking.NOT_FOUND)

        if not request.user.is_staff and booking.user != request.user:
            raise QuickBookException(Errors.Auth.PERMISSION_DENIED)

        # Booking updating via status endpoint or serializer
        return Response(BookingSerializer(booking).data)


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get(self, request, pk):
        booking = get_booking_by_id(pk)

        if booking is None:
            raise QuickBookException(Errors.Booking.NOT_FOUND)

        if not request.user.is_staff and booking.user != request.user:
            raise QuickBookException(Errors.Auth.PERMISSION_DENIED)

        return Response(BookingSerializer(booking).data)


class BookingStatusView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = BookingStatusSerializer

    @ratelimit_sensitive()
    def patch(self, request, pk):
        serializer = BookingStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = update_booking_status(
            booking_id=pk,
            new_status=serializer.validated_data[BookingFields.STATUS],
            requesting_user=request.user,
            action=action,
        )

        if result is None:
            return Response({"message": Messages.Validation.SUCCESS, "action": action}, status=status.HTTP_200_OK)
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)

        return Response(BookingSerializer(result).data)


class BookingListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get(self, request):
        status_param = request.query_params.get(BookingFields.FILTER_STATUS)
        event_param  = request.query_params.get(BookingFields.FILTER_EVENT)
        user_param   = request.query_params.get(BookingFields.FILTER_USER)

        target_user = (user_param if user_param else None) if request.user.is_staff else request.user

        paginator = StandardResultsPagination()
        bookings = get_all_bookings(
            user=target_user,
            status=status_param,
            event=event_param,
        )

        page = paginator.paginate_queryset(bookings, request)
        serializer = BookingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BookingCleanupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        released_count = cleanup_expired_pending_bookings()
        return Response(
            {
                "message": f"Successfully released {released_count} expired pending booking(s).",
                "released_count": released_count,
            },
            status=status.HTTP_200_OK,
        )

