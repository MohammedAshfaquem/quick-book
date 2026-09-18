from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.constants import AuthNames, AuthUrls
from apps.authentication.views import CurrentUserView, LoginView, LogoutView, RegisterView, UserListView

urlpatterns = [
    # Registration & Login
    path(AuthUrls.REGISTER, RegisterView.as_view(), name=AuthNames.REGISTER),
    path(AuthUrls.LOGIN, LoginView.as_view(), name=AuthNames.LOGIN),
    path(AuthUrls.LOGOUT, LogoutView.as_view(), name=AuthNames.LOGOUT),

    # JWT token refresh (built-in simplejwt view)
    path(AuthUrls.TOKEN_REFRESH, TokenRefreshView.as_view(), name=AuthNames.TOKEN_REFRESH),

    # Logged-in user profile
    path(AuthUrls.CURRENT_USER, CurrentUserView.as_view(), name=AuthNames.CURRENT_USER),
    path(AuthUrls.USERS_LIST, UserListView.as_view(), name=AuthNames.USERS_LIST),
]
