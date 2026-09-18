"""
Tests for Event model, selectors, services, and views.
"""

from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.authentication.models import User
from apps.vendors.models import Vendor
from apps.events.models import Event
from apps.events.services import create_event, update_event, set_event_status
from apps.events.selectors import get_all_events, get_upcoming_events


class EventModuleTests(APITestCase):
    def setUp(self):
        self.staff_user = User.objects.create_staff_user(
            email="staff@example.com",
            password="Password123!",
            first_name="Staff",
            last_name="User",
        )
        self.regular_user = User.objects.create_customer_user(
            email="customer@example.com",
            password="Password123!",
            first_name="Customer",
            last_name="User",
        )
        self.vendor = Vendor.objects.create(
            company_name="TechConf Inc",
            contact_email="contact@techconf.com",
            contact_phone="+1234567890",
        )
        now = timezone.now()
        self.event = Event.objects.create(
            vendor=self.vendor,
            title="Tech Summit 2026",
            description="Annual tech conference",
            venue="Main Hall",
            start_date=now + timedelta(days=10),
            end_date=now + timedelta(days=12),
            booking_start_date=now - timedelta(days=1),
            booking_end_date=now + timedelta(days=9),
            total_seats=100,
            available_seats=100,
            price=299.99,
        )

    def test_event_properties(self):
        """Test is_upcoming, is_ongoing, is_booking_open, is_sold_out properties."""
        self.assertTrue(self.event.is_upcoming)
        self.assertFalse(self.event.is_ongoing)
        self.assertTrue(self.event.is_booking_open)
        self.assertFalse(self.event.is_sold_out)

    def test_create_event_service(self):
        """Test create_event service sets available_seats equal to total_seats."""
        now = timezone.now()
        data = {
            "vendor": self.vendor,
            "title": "AI Expo",
            "description": "AI developments",
            "venue": "Expo Center",
            "start_date": now + timedelta(days=20),
            "end_date": now + timedelta(days=22),
            "booking_start_date": now + timedelta(days=1),
            "total_seats": 50,
            "price": 150.00,
        }
        event = create_event(data)
        self.assertEqual(event.available_seats, 50)
        self.assertEqual(event.title, "AI Expo")

    def test_event_list_api_public(self):
        """Public users can list active events."""
        response = self.client.get("/api/v1/events/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_event_list_filter_by_name(self):
        """Filtering event list by name query param."""
        response = self.client.get("/api/v1/events/list/?name=Tech")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get("/api/v1/events/list/?name=NonExistent")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_create_event_api_staff_required(self):
        """Non-staff users cannot create events."""
        self.client.force_authenticate(user=self.regular_user)
        now = timezone.now()
        payload = {
            "vendor": str(self.vendor.id),
            "title": "Music Fest",
            "venue": "Arena",
            "start_date": (now + timedelta(days=30)).isoformat(),
            "end_date": (now + timedelta(days=31)).isoformat(),
            "booking_start_date": (now + timedelta(days=5)).isoformat(),
            "total_seats": 200,
            "price": "99.00",
        }
        response = self.client.post("/api/v1/events/create/", payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post("/api/v1/events/create/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Music Fest")
        self.assertEqual(response.data["available_seats"], 200)

    def test_invalid_date_validations(self):
        """End date before start date should fail validation."""
        self.client.force_authenticate(user=self.staff_user)
        now = timezone.now()
        payload = {
            "vendor": str(self.vendor.id),
            "title": "Bad Date Event",
            "venue": "Hall B",
            "start_date": (now + timedelta(days=30)).isoformat(),
            "end_date": (now + timedelta(days=20)).isoformat(),  # invalid!
            "booking_start_date": (now + timedelta(days=5)).isoformat(),
            "total_seats": 50,
            "price": "50.00",
        }
        response = self.client.post("/api/v1/events/create/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", response.data)
