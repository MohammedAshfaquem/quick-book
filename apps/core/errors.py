from rest_framework import status


class Errors:
    """Root error catalog — grouped by domain."""

    class Auth:
        """Authentication and user errors."""

        INVALID_CREDENTIALS = {
            "code": "quickbook_auth_00001",
            "message": "Invalid email or password.",
            "status_code": status.HTTP_401_UNAUTHORIZED,
        }
        REFERRAL_CODE_NOT_FOUND = {
            "code": "quickbook_auth_00002",
            "message": "The referral code provided does not exist.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        REFERRER_INACTIVE = {
            "code": "quickbook_auth_00007",
            "message": "The referral code belongs to a deactivated account.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        ACCOUNT_DEACTIVATED = {
            "code": "quickbook_auth_00003",
            "message": "This account has been deactivated.",
            "status_code": status.HTTP_401_UNAUTHORIZED,
        }
        USER_NOT_FOUND = {
            "code": "quickbook_auth_00004",
            "message": "User not found.",
            "status_code": status.HTTP_404_NOT_FOUND,
        }
        MISSING_REFRESH_TOKEN = {
            "code": "quickbook_auth_00005",
            "message": "Refresh token is required.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        INVALID_TOKEN = {
            "code": "quickbook_auth_00006",
            "message": "Token is invalid or already blacklisted.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        PERMISSION_DENIED = {
            "code": "quickbook_auth_00008",
            "message": "You do not have permission to perform this action.",
            "status_code": status.HTTP_403_FORBIDDEN,
        }
        INCORRECT_CURRENT_PASSWORD = {
            "code": "quickbook_auth_00009",
            "message": "Current password is incorrect.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }

    class Event:
        """Event domain errors."""

        NOT_FOUND = {
            "code": "quickbook_event_00001",
            "message": "Event not found.",
            "status_code": status.HTTP_404_NOT_FOUND,
        }
        EXPIRED = {
            "code": "quickbook_event_00002",
            "message": "This event has already passed.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        FULLY_BOOKED = {
            "code": "quickbook_event_00003",
            "message": "No seats available for this event.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        INACTIVE = {
            "code": "quickbook_event_00004",
            "message": "Cannot book an inactive event.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }

    class Booking:
        """Booking domain errors."""

        NOT_FOUND = {
            "code": "quickbook_booking_00001",
            "message": "Booking not found.",
            "status_code": status.HTTP_404_NOT_FOUND,
        }
        PERMISSION_DENIED = {
            "code": "quickbook_booking_00002",
            "message": "You do not have permission to perform this action.",
            "status_code": status.HTTP_403_FORBIDDEN,
        }
        ALREADY_CANCELLED = {
            "code": "quickbook_booking_00003",
            "message": "This booking has already been cancelled.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        CANNOT_CANCEL_PAST_EVENT = {
            "code": "quickbook_booking_00004",
            "message": "Cannot cancel a booking for an event that has already passed.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        INVALID_TICKET_COUNT = {
            "code": "quickbook_booking_00005",
            "message": "Ticket count must be at least 1.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        BOOKING_CLOSED = {
            "code": "quickbook_booking_00006",
            "message": "Booking is currently closed for this event.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        NOT_ENOUGH_SEATS = {
            "code": "quickbook_booking_00007",
            "message": "Not enough seats available for this event.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        MIN_SEATS_NOT_MET = {
            "code": "quickbook_booking_00008",
            "message": "At least {min_seats} seat(s) required per booking.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }
        MAX_SEATS_EXCEEDED = {
            "code": "quickbook_booking_00009",
            "message": "Maximum limit reached. You can book at most {max_seats} seat(s) per booking.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }

    class Vendor:
        """Vendor domain errors."""

        NOT_FOUND = {
            "code": "quickbook_vendor_00001",
            "message": "Vendor not found.",
            "status_code": status.HTTP_404_NOT_FOUND,
        }
        ALREADY_EXISTS = {
            "code": "quickbook_vendor_00002",
            "message": "A vendor profile already exists for this user.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }

    class Referral:
        """Referral tree errors."""

        USER_NOT_FOUND = {
            "code": "quickbook_referral_00001",
            "message": "User not found in the referral network.",
            "status_code": status.HTTP_404_NOT_FOUND,
        }
        TREE_EMPTY = {
            "code": "quickbook_referral_00002",
            "message": "This user has no referral tree.",
            "status_code": status.HTTP_404_NOT_FOUND,
        }

    class Params:
        """Parameter and request validation errors."""

        INVALID_PARAMS = {
            "code": "quickbook_params_00001",
            "message": "Invalid parameters passed.",
            "status_code": status.HTTP_400_BAD_REQUEST,
        }

