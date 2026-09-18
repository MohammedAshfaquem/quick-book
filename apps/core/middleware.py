from django.conf import settings
from django.http import JsonResponse
from rest_framework import status


class ModuleFeatureToggleMiddleware:
    """
    Middleware that checks whether an API module is enabled in settings.FEATURE_FLAGS.

    Route prefixes and corresponding flags:
        /api/v1/events/    → EVENT_MODULE
        /api/v1/bookings/  → BOOKING_MODULE
        /api/v1/vendors/   → VENDOR_MODULE
        /api/v1/referrals/ → REFERRAL_MODULE
    """

    PATH_FLAG_MAPPING = {
        "/api/v1/events/":    "EVENT_MODULE",
        "/api/v1/bookings/":  "BOOKING_MODULE",
        "/api/v1/vendors/":   "VENDOR_MODULE",
        "/api/v1/referrals/": "REFERRAL_MODULE",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        for prefix, flag_name in self.PATH_FLAG_MAPPING.items():
            if path.startswith(prefix):
                enabled = getattr(settings, "FEATURE_FLAGS", {}).get(flag_name, True)
                if not enabled:
                    module_name = flag_name.replace("_MODULE", "").capitalize()
                    return JsonResponse(
                        {
                            "code": "quickbook_feature_disabled",
                            "message": f"The {module_name} module is currently disabled by administrator configuration.",
                            "status_code": status.HTTP_403_FORBIDDEN,
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        return self.get_response(request)
