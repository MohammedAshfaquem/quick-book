"""
Root URL configuration for QuickBook.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Root redirect to Staff Dashboard
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),

    # Django Admin (kept for superuser access only)
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/vendors/", include("apps.vendors.urls")),
    path("api/v1/events/", include("apps.events.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),
    path("api/v1/referrals/", include("apps.referrals.urls")),

    # Swagger / OpenAPI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Custom Staff Dashboard (HTML, session-based)
    path("dashboard/", include("apps.dashboard.urls")),
]
