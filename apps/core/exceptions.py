from django_ratelimit.exceptions import Ratelimited
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


class QuickBookException(Exception):

    def __init__(self, error: dict, message: str | None = None):
        self.error_code = error.get("code", "quickbook_00000")
        self.message = message or error.get("message", "An unexpected error occurred.")
        self.status_code = error.get("status_code", 400)
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Global DRF Exception Handler
# ---------------------------------------------------------------------------

def custom_exception_handler(exc, context):
    if isinstance(exc, QuickBookException):
        return Response(
            {
                "code": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
            },
            status=exc.status_code,
        )

    if isinstance(exc, Ratelimited):
        return Response(
            {
                "code": "quickbook_rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
                "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Fall back to DRF default for serializer validation errors
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "code": "quickbook_validation_error",
            "message": response.data,
            "status_code": response.status_code,
        }

    return response
