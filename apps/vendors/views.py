from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import ActionType
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.messages import Messages
from apps.core.pagination import StandardResultsPagination
from apps.core.permissions import IsStaffUser
from apps.vendors.constants import VendorFields
from apps.vendors.selectors import get_all_vendors, get_vendor_by_id
from apps.vendors.serializers import (
    VendorSerializer,
    VendorStatusSerializer,
    VendorUpdateSerializer,
)
from apps.vendors.services import create_vendor, set_vendor_status, update_vendor


class VendorListView(APIView):

    permission_classes = [IsStaffUser]
    serializer_class = VendorSerializer

    def get(self, request):
        name   = request.query_params.get(VendorFields.FILTER_NAME)
        status_filter = request.query_params.get(VendorFields.FILTER_STATUS)

        paginator = StandardResultsPagination()
        vendors = get_all_vendors(name=name, status=status_filter)
        page = paginator.paginate_queryset(vendors, request)
        serializer = VendorSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class VendorCreateView(APIView):

    permission_classes = [IsStaffUser]
    serializer_class = VendorSerializer

    def post(self, request):
        """Create a new vendor."""
        serializer = VendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = create_vendor(serializer.validated_data, action=action)

        if result is None:
            return Response({"message": Messages.Validation.SUCCESS, "action": action}, status=status.HTTP_200_OK)

        return Response(
            VendorSerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class VendorDetailView(APIView):

    permission_classes = [IsStaffUser]
    serializer_class = VendorSerializer

    def get(self, request, pk):
        vendor = get_vendor_by_id(pk)

        if vendor is None:
            raise QuickBookException(Errors.Vendor.NOT_FOUND)

        return Response(VendorSerializer(vendor).data)


class VendorUpdateView(APIView):

    permission_classes = [IsStaffUser]
    serializer_class = VendorUpdateSerializer

    def patch(self, request, pk):
        """Partially update vendor details."""
        vendor = get_vendor_by_id(pk)

        if vendor is None:
            raise QuickBookException(Errors.Vendor.NOT_FOUND)

        serializer = VendorUpdateSerializer(vendor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = update_vendor(pk, serializer.validated_data, action=action)

        if result is None:
            return Response({"message": Messages.Validation.SUCCESS, "action": action}, status=status.HTTP_200_OK)
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)

        return Response(VendorSerializer(result).data)


class VendorStatusView(APIView):

    permission_classes = [IsStaffUser]
    serializer_class = VendorStatusSerializer

    def patch(self, request, pk):
        serializer = VendorStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = request.query_params.get("action") or request.data.get("action") or ActionType.CONFIRM
        result = set_vendor_status(
            vendor_id=pk,
            is_active=serializer.validated_data[VendorFields.IS_ACTIVE],
            action=action,
        )

        if result is None:
            return Response({"message": Messages.Validation.SUCCESS, "action": action}, status=status.HTTP_200_OK)
        if isinstance(result, dict):
            return Response(result, status=status.HTTP_200_OK)

        return Response(VendorSerializer(result).data)

