from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError

from apps.authentication.constants import JWTFields, UserFields
from apps.authentication.selectors import get_all_users
from apps.authentication.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)
from apps.authentication.services import login_user, logout_user, register_user
from apps.core.constants import FilterParams
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.messages import Messages
from apps.core.pagination import StandardResultsPagination
from apps.core.throttling import ratelimit_login, ratelimit_register


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @ratelimit_register()
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, tokens = register_user(serializer.validated_data)

        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @ratelimit_login()
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, tokens = login_user(
            email=serializer.validated_data[UserFields.EMAIL],
            password=serializer.validated_data[UserFields.PASSWORD],
        )

        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data[JWTFields.REFRESH]

        try:
            logout_user(refresh_token)
        except TokenError:
            raise QuickBookException(Errors.Auth.INVALID_TOKEN)

        return Response(
            {"message": Messages.Auth.LOGOUT_SUCCESS},
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        status_filter = request.query_params.get(FilterParams.STATUS)
        paginator = StandardResultsPagination()
        users = get_all_users(status=status_filter)
        page = paginator.paginate_queryset(users, request)
        serializer = UserProfileSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

