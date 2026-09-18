"""
Unit tests for authentication services.

Tests pure business logic — no HTTP, no views.
"""

from django.test import TestCase

from apps.authentication.models import User
from apps.authentication.services import get_tokens_for_user, login_user, register_user
from apps.core.exceptions import InvalidCredentialsException, ReferralCodeNotFoundException


class RegisterUserServiceTest(TestCase):
    """Tests for register_user() service function."""

    def _valid_payload(self, **overrides) -> dict:
        """Return a valid registration payload."""
        data = {
            "email": "alice@example.com",
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Smith",
            "password": "StrongPass@123",
        }
        data.update(overrides)
        return data

    def test_register_creates_user(self):
        """Registering with valid data creates a User record."""
        user, tokens = register_user(self._valid_payload())

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "alice@example.com")

    def test_register_auto_generates_referral_code(self):
        """Every new user gets a non-empty referral code."""
        user, _ = register_user(self._valid_payload())

        self.assertTrue(bool(user.referral_code))
        self.assertEqual(len(user.referral_code), 8)

    def test_register_returns_jwt_tokens(self):
        """Registration response includes access and refresh tokens."""
        _, tokens = register_user(self._valid_payload())

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_register_with_valid_referral_code(self):
        """Registering with a valid referral code sets referred_by."""
        referrer, _ = register_user(self._valid_payload(email="ref@example.com", username="ref"))

        new_user, _ = register_user(
            self._valid_payload(
                email="bob@example.com",
                username="bob",
                referral_code=referrer.referral_code,
            )
        )

        self.assertEqual(new_user.referred_by, referrer)

    def test_register_with_invalid_referral_code_raises(self):
        """Registering with a non-existent referral code raises ReferralCodeNotFoundException."""
        with self.assertRaises(ReferralCodeNotFoundException):
            register_user(self._valid_payload(referral_code="BADCODE1"))

    def test_register_without_referral_code_has_no_referrer(self):
        """Registering without a referral code leaves referred_by as None."""
        user, _ = register_user(self._valid_payload())

        self.assertIsNone(user.referred_by)

    def test_password_is_hashed(self):
        """Raw password should never be stored — always hashed."""
        user, _ = register_user(self._valid_payload(password="StrongPass@123"))

        self.assertNotEqual(user.password, "StrongPass@123")
        self.assertTrue(user.check_password("StrongPass@123"))


class LoginUserServiceTest(TestCase):
    """Tests for login_user() service function."""

    def setUp(self):
        """Create a test user before each test."""
        self.user, _ = register_user(
            {
                "email": "login@example.com",
                "username": "loginuser",
                "password": "StrongPass@123",
            }
        )

    def test_login_with_correct_credentials(self):
        """Valid email + password returns user and tokens."""
        user, tokens = login_user("login@example.com", "StrongPass@123")

        self.assertEqual(user.email, "login@example.com")
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_login_with_wrong_password_raises(self):
        """Wrong password raises InvalidCredentialsException."""
        with self.assertRaises(InvalidCredentialsException):
            login_user("login@example.com", "WrongPassword")

    def test_login_with_wrong_email_raises(self):
        """Non-existent email raises InvalidCredentialsException."""
        with self.assertRaises(InvalidCredentialsException):
            login_user("nobody@example.com", "StrongPass@123")

    def test_login_inactive_user_raises(self):
        """Deactivated account raises InvalidCredentialsException."""
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(InvalidCredentialsException):
            login_user("login@example.com", "StrongPass@123")


class GetTokensServiceTest(TestCase):
    """Tests for get_tokens_for_user() helper."""

    def test_tokens_have_access_and_refresh_keys(self):
        """Token dict always has access and refresh keys."""
        user = User.objects.create_user(
            email="tok@example.com", username="tok", password="pass"
        )
        tokens = get_tokens_for_user(user)

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_tokens_are_strings(self):
        """Both tokens should be non-empty strings."""
        user = User.objects.create_user(
            email="tok2@example.com", username="tok2", password="pass"
        )
        tokens = get_tokens_for_user(user)

        self.assertIsInstance(tokens["access"], str)
        self.assertIsInstance(tokens["refresh"], str)
        self.assertTrue(len(tokens["access"]) > 0)
