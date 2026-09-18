"""
API integration tests for authentication endpoints.

Tests the full HTTP request → response cycle.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.authentication.constants import AuthNames
from apps.authentication.models import User
from apps.authentication.services import register_user


class RegisterAPITest(APITestCase):
    """Tests for POST /api/v1/auth/register/"""

    def setUp(self):
        """Set up reusable URL and payload."""
        self.url = reverse(AuthNames.REGISTER)
        self.valid_payload = {
            "email": "alice@example.com",
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Smith",
            "password": "StrongPass@123",
            "password_confirm": "StrongPass@123",
        }

    def test_register_success_returns_201(self):
        """Valid registration returns 201 with user and tokens."""
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data["data"])
        self.assertIn("tokens", response.data["data"])

    def test_register_creates_user_in_db(self):
        """Successful registration creates a User record."""
        self.client.post(self.url, self.valid_payload, format="json")

        self.assertTrue(User.objects.filter(email="alice@example.com").exists())

    def test_register_password_mismatch_returns_400(self):
        """Mismatched passwords return 400."""
        payload = {**self.valid_payload, "password_confirm": "DifferentPass@123"}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email_returns_400(self):
        """Registering with an already used email returns 400."""
        self.client.post(self.url, self.valid_payload, format="json")
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_referral_code_returns_400(self):
        """Invalid referral code returns 400 with proper error code."""
        payload = {**self.valid_payload, "referral_code": "BADCODE1"}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "REFERRAL_CODE_NOT_FOUND")

    def test_register_missing_email_returns_400(self):
        """Missing email field returns 400."""
        payload = {**self.valid_payload}
        payload.pop("email")
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(APITestCase):
    """Tests for POST /api/v1/auth/login/"""

    def setUp(self):
        """Create a user and set up login URL."""
        self.url = reverse(AuthNames.LOGIN)
        register_user(
            {
                "email": "user@example.com",
                "username": "testuser",
                "password": "StrongPass@123",
            }
        )

    def test_login_success_returns_200(self):
        """Valid credentials return 200 with access and refresh tokens."""
        response = self.client.post(
            self.url,
            {"email": "user@example.com", "password": "StrongPass@123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertIn("refresh", response.data["data"]["tokens"])

    def test_login_wrong_password_returns_401(self):
        """Wrong password returns 401."""
        response = self.client.post(
            self.url,
            {"email": "user@example.com", "password": "WrongPass"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email_returns_401(self):
        """Unknown email returns 401."""
        response = self.client.post(
            self.url,
            {"email": "ghost@example.com", "password": "StrongPass@123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeAPITest(APITestCase):
    """Tests for GET /api/v1/auth/me/"""

    def setUp(self):
        """Create and authenticate a user."""
        self.url = reverse(AuthNames.ME)
        user, tokens = register_user(
            {
                "email": "me@example.com",
                "username": "meuser",
                "password": "StrongPass@123",
            }
        )
        self.user = user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    def test_me_returns_user_profile(self):
        """Authenticated request returns the logged-in user's profile."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], "me@example.com")

    def test_me_unauthenticated_returns_401(self):
        """Unauthenticated request returns 401."""
        self.client.credentials()  # clear auth
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutAPITest(APITestCase):
    """Tests for POST /api/v1/auth/logout/"""

    def setUp(self):
        """Create a user and get tokens."""
        self.url = reverse(AuthNames.LOGOUT)
        user, tokens = register_user(
            {
                "email": "out@example.com",
                "username": "logoutuser",
                "password": "StrongPass@123",
            }
        )
        self.tokens = tokens
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    def test_logout_success_returns_200(self):
        """Logout with valid refresh token returns 200."""
        response = self.client.post(
            self.url, {"refresh": self.tokens["refresh"]}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_missing_refresh_token_returns_400(self):
        """Logout without refresh token returns 400."""
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_blacklisted_token_returns_400(self):
        """Using an already-blacklisted token returns 400."""
        # first logout
        self.client.post(self.url, {"refresh": self.tokens["refresh"]}, format="json")
        # second logout with same token
        response = self.client.post(
            self.url, {"refresh": self.tokens["refresh"]}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
