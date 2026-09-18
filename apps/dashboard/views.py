from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.views import View

from apps.authentication.constants import UserFields
from apps.authentication.models import User
from apps.bookings.constants import BookingFields, BookingStatus
from apps.bookings.models import Booking
from apps.bookings.services import update_booking_status
from apps.core.constants import CommonFields, FilterParams
from apps.core.messages import Messages
from apps.events.constants import EventFields
from apps.events.models import Event
from apps.events.serializers import validate_event_dates
from apps.vendors.constants import VendorFields
from apps.vendors.models import Vendor
from rest_framework import serializers

def parse_aware(value):
    dt = parse_datetime(value) if value else None
    return make_aware(dt) if dt is not None else None


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("dashboard:login")
        messages.error(self.request, Messages.Auth.STAFF_REQUIRED)
        return redirect("dashboard:login")


# ---------------------------------------------------------------------------
# Auth Views
# ---------------------------------------------------------------------------

class DashboardLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("dashboard:overview")
        return render(request, "dashboard/auth/login.html")

    def post(self, request):
        login_input = request.POST.get(UserFields.EMAIL, "").strip()
        password = request.POST.get(UserFields.PASSWORD)

        user = authenticate(request, username=login_input, password=password)

        if user is None and login_input:
            from django.db.models import Q
            try:
                found_user = User.objects.get(Q(email__iexact=login_input) | Q(username__iexact=login_input))
                user = authenticate(request, username=found_user.email, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, Messages.Auth.WELCOME_BACK.format(email=user.email))
            return redirect("dashboard:overview")
        else:
            messages.error(request, Messages.Auth.INVALID_CREDENTIALS)
            return render(request, "dashboard/auth/login.html")


class DashboardLogoutView(View):
    """Staff logout view."""

    def get(self, request):
        logout(request)
        messages.success(request, Messages.Auth.LOGOUT_SUCCESS)
        return redirect("dashboard:login")


# ---------------------------------------------------------------------------
# Overview View
# ---------------------------------------------------------------------------

class DashboardOverviewView(StaffRequiredMixin, View):
    def get(self, request):
        context = {
            "total_customers": User.objects.filter(is_staff=False).count(),
            "total_vendors": Vendor.objects.filter(is_active=True).count(),
            "total_events": Event.objects.filter(is_active=True).count(),
            "successful_bookings": Booking.objects.filter(status=BookingStatus.CONFIRMED).count(),
            "total_bookings": Booking.objects.count(),
            "recent_bookings": Booking.objects.select_related("user", "event").order_by("-created_at")[:8],
        }
        return render(request, "dashboard/overview.html", context)


# ---------------------------------------------------------------------------
# Vendor Views
# ---------------------------------------------------------------------------

class VendorListView(StaffRequiredMixin, View):
    def get(self, request):
        search = request.GET.get(FilterParams.SEARCH, "")
        status_filter = request.GET.get("status", "")
        qs = Vendor.objects.all()

        if search:
            qs = qs.filter(company_name__icontains=search) | qs.filter(contact_email__icontains=search)

        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)

        return render(request, "dashboard/vendors/list.html", {"vendors": qs.order_by("-created_at")})


class VendorAddView(StaffRequiredMixin, View):
    def get(self, request):
        return render(request, "dashboard/vendors/form.html", {"vendor": None})

    def post(self, request):
        company_name = request.POST.get(VendorFields.COMPANY_NAME)
        contact_email = request.POST.get(VendorFields.CONTACT_EMAIL, "").strip()
        contact_phone = request.POST.get(VendorFields.CONTACT_PHONE)
        description = request.POST.get(VendorFields.DESCRIPTION, "")
        logo_url = request.POST.get(VendorFields.LOGO_URL, "")
        is_active = request.POST.get(CommonFields.IS_ACTIVE) == "on"

        if Vendor.objects.filter(contact_email__iexact=contact_email).exists():
            messages.error(request, Messages.Vendor.EMAIL_EXISTS.format(email=contact_email))
            return render(request, "dashboard/vendors/form.html", {"vendor": None})

        try:
            Vendor.objects.create(
                company_name=company_name,
                contact_email=contact_email,
                contact_phone=contact_phone,
                description=description,
                logo_url=logo_url,
                is_active=is_active,
            )
        except IntegrityError:
            messages.error(request, Messages.Vendor.EMAIL_EXISTS.format(email=contact_email))
            return render(request, "dashboard/vendors/form.html", {"vendor": None})

        messages.success(request, Messages.Vendor.CREATED_NAME_SUCCESS.format(company_name=company_name))
        return redirect("dashboard:vendor-list")


class VendorEditView(StaffRequiredMixin, View):
    def get(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        return render(request, "dashboard/vendors/form.html", {"vendor": vendor})

    def post(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        company_name = request.POST.get(VendorFields.COMPANY_NAME)
        contact_email = request.POST.get(VendorFields.CONTACT_EMAIL, "").strip()
        contact_phone = request.POST.get(VendorFields.CONTACT_PHONE)
        description = request.POST.get(VendorFields.DESCRIPTION, "")
        logo_url = request.POST.get(VendorFields.LOGO_URL, "")
        is_active = request.POST.get(CommonFields.IS_ACTIVE) == "on"

        if Vendor.objects.filter(contact_email__iexact=contact_email).exclude(pk=vendor.pk).exists():
            messages.error(request, Messages.Vendor.EMAIL_EXISTS.format(email=contact_email))
            return render(request, "dashboard/vendors/form.html", {"vendor": vendor})

        try:
            vendor.company_name = company_name
            vendor.contact_email = contact_email
            vendor.contact_phone = contact_phone
            vendor.description = description
            vendor.logo_url = logo_url
            vendor.is_active = is_active
            vendor.save()
        except IntegrityError:
            messages.error(request, Messages.Vendor.EMAIL_EXISTS.format(email=contact_email))
            return render(request, "dashboard/vendors/form.html", {"vendor": vendor})

        messages.success(request, Messages.Vendor.UPDATED_NAME_SUCCESS.format(company_name=vendor.company_name))
        return redirect("dashboard:vendor-list")


class VendorToggleStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        vendor = get_object_or_404(Vendor, pk=pk)
        vendor.is_active = not vendor.is_active
        vendor.save()
        status_label = "Active" if vendor.is_active else "Inactive"
        messages.success(request, Messages.Vendor.STATUS_UPDATED.format(company_name=vendor.company_name, status=status_label))
        return redirect("dashboard:vendor-list")


class VendorDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        from apps.bookings.models import Booking
        from apps.events.models import Event
        from django.db.models import Sum

        vendor = get_object_or_404(Vendor, pk=pk)
        vendor_events = Event.objects.filter(vendor=vendor).order_by("-created_at")

        active_events_count = vendor_events.filter(is_active=True).count()
        total_seats_hosted = vendor_events.aggregate(total=Sum("total_seats"))["total"] or 0
        total_bookings_count = Booking.objects.filter(event__vendor=vendor).count()

        context = {
            "vendor": vendor,
            "vendor_events": vendor_events,
            "active_events_count": active_events_count,
            "total_seats_hosted": total_seats_hosted,
            "total_bookings_count": total_bookings_count,
        }
        return render(request, "dashboard/vendors/detail.html", context)


# ---------------------------------------------------------------------------
# Event Views
# ---------------------------------------------------------------------------

class EventListView(StaffRequiredMixin, View):
    def get(self, request):
        from django.utils import timezone
        from django.db.models import Q
        from apps.events.constants import ShowStatus

        search       = request.GET.get(FilterParams.SEARCH, "")
        status_filter     = request.GET.get("status", "")
        show_status_filter = request.GET.get("show_status", "")
        qs = Event.objects.select_related("vendor").all()

        if search:
            qs = qs.filter(title__icontains=search)

        if status_filter == "active":
            qs = qs.filter(is_active=True)
        elif status_filter == "inactive":
            qs = qs.filter(is_active=False)

        if show_status_filter:
            now = timezone.now()
            if show_status_filter == ShowStatus.EXPIRED:
                qs = qs.filter(show_end_date__lte=now)
            elif show_status_filter == ShowStatus.RUNNING:
                qs = qs.filter(show_start_date__lte=now, show_end_date__gt=now)
            elif show_status_filter == ShowStatus.BOOKING_ENABLED:
                qs = qs.filter(
                    booking_start_date__lte=now,
                    show_start_date__gt=now,
                ).filter(Q(booking_end_date__isnull=True) | Q(booking_end_date__gt=now))
            elif show_status_filter == ShowStatus.UPCOMING:
                qs = qs.filter(booking_start_date__gt=now)

        return render(request, "dashboard/events/list.html", {"events": qs.order_by("-start_date")})



class EventAddView(StaffRequiredMixin, View):
    def get(self, request):
        vendors = Vendor.objects.filter(is_active=True)
        return render(request, "dashboard/events/form.html", {"event": None, "vendors": vendors})

    def post(self, request):
        vendor_id = request.POST.get("vendor_id")
        title = request.POST.get(EventFields.TITLE)
        description = request.POST.get(EventFields.DESCRIPTION, "")
        venue = request.POST.get(EventFields.VENUE)
        banner_url = request.POST.get(EventFields.BANNER_URL, "")

        start_date = parse_aware(request.POST.get(EventFields.START_DATE))
        end_date = parse_aware(request.POST.get(EventFields.END_DATE))
        booking_start_date = parse_aware(request.POST.get(EventFields.BOOKING_START_DATE))
        booking_end_date = parse_aware(request.POST.get(EventFields.BOOKING_END_DATE))
        show_start_raw = request.POST.get(EventFields.SHOW_START_DATE)
        show_end_raw = request.POST.get(EventFields.SHOW_END_DATE)
        show_start_date = parse_aware(show_start_raw) if show_start_raw else start_date
        show_end_date = parse_aware(show_end_raw) if show_end_raw else end_date

        total_seats = int(request.POST.get(EventFields.TOTAL_SEATS, 100))
        min_seats_per_booking = int(request.POST.get(EventFields.MIN_SEATS_PER_BOOKING, 1))
        max_seats_per_booking = int(request.POST.get(EventFields.MAX_SEATS_PER_BOOKING, 10))
        price = float(request.POST.get(EventFields.PRICE, 0))
        is_active = request.POST.get(CommonFields.IS_ACTIVE) == "on"

        attrs = {
            EventFields.VENUE: venue,
            EventFields.START_DATE: start_date,
            EventFields.END_DATE: end_date,
            EventFields.BOOKING_START_DATE: booking_start_date,
            EventFields.BOOKING_END_DATE: booking_end_date,
            EventFields.SHOW_START_DATE: show_start_date,
            EventFields.SHOW_END_DATE: show_end_date,
            EventFields.TOTAL_SEATS: total_seats,
            EventFields.MIN_SEATS_PER_BOOKING: min_seats_per_booking,
            EventFields.MAX_SEATS_PER_BOOKING: max_seats_per_booking,
        }

        try:
            validate_event_dates(attrs)
        except serializers.ValidationError as exc:
            for field, err in exc.detail.items():
                msg = err[0] if isinstance(err, list) else str(err)
                messages.error(request, msg)
            vendors = Vendor.objects.filter(is_active=True)
            return render(request, "dashboard/events/form.html", {"event": None, "vendors": vendors})

        vendor = get_object_or_404(Vendor, pk=vendor_id)

        Event.objects.create(
            vendor=vendor,
            title=title,
            description=description,
            venue=venue,
            banner_url=banner_url,
            start_date=start_date,
            end_date=end_date,
            booking_start_date=booking_start_date,
            booking_end_date=booking_end_date,
            show_start_date=show_start_date,
            show_end_date=show_end_date,
            total_seats=total_seats,
            available_seats=total_seats,
            min_seats_per_booking=min_seats_per_booking,
            max_seats_per_booking=max_seats_per_booking,
            price=price,
            is_active=is_active,
        )
        messages.success(request, Messages.Event.CREATED_TITLE_SUCCESS.format(title=title))
        return redirect("dashboard:event-list")


class EventEditView(StaffRequiredMixin, View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        vendors = Vendor.objects.filter(is_active=True)
        return render(request, "dashboard/events/form.html", {"event": event, "vendors": vendors})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        vendor_id = request.POST.get("vendor_id")
        event.vendor = get_object_or_404(Vendor, pk=vendor_id)
        event.title = request.POST.get(EventFields.TITLE)
        event.description = request.POST.get(EventFields.DESCRIPTION, "")
        event.venue = request.POST.get(EventFields.VENUE)
        event.banner_url = request.POST.get(EventFields.BANNER_URL, "")

        event.start_date = parse_aware(request.POST.get(EventFields.START_DATE)) or event.start_date
        event.end_date = parse_aware(request.POST.get(EventFields.END_DATE)) or event.end_date
        event.booking_start_date = parse_aware(request.POST.get(EventFields.BOOKING_START_DATE)) or event.booking_start_date
        booking_end_raw = request.POST.get(EventFields.BOOKING_END_DATE)
        event.booking_end_date = parse_aware(booking_end_raw) if booking_end_raw else event.booking_end_date
        show_start_raw = request.POST.get(EventFields.SHOW_START_DATE)
        show_end_raw = request.POST.get(EventFields.SHOW_END_DATE)
        if show_start_raw:
            event.show_start_date = parse_aware(show_start_raw)
        if show_end_raw:
            event.show_end_date = parse_aware(show_end_raw)

        event.min_seats_per_booking = int(request.POST.get(EventFields.MIN_SEATS_PER_BOOKING, event.min_seats_per_booking))
        event.max_seats_per_booking = int(request.POST.get(EventFields.MAX_SEATS_PER_BOOKING, event.max_seats_per_booking))
        event.price = float(request.POST.get(EventFields.PRICE, 0))
        event.is_active = request.POST.get(CommonFields.IS_ACTIVE) == "on"

        attrs = {
            EventFields.VENUE: event.venue,
            EventFields.START_DATE: event.start_date,
            EventFields.END_DATE: event.end_date,
            EventFields.BOOKING_START_DATE: event.booking_start_date,
            EventFields.BOOKING_END_DATE: event.booking_end_date,
            EventFields.SHOW_START_DATE: event.show_start_date,
            EventFields.SHOW_END_DATE: event.show_end_date,
            EventFields.TOTAL_SEATS: event.total_seats,
            EventFields.MIN_SEATS_PER_BOOKING: event.min_seats_per_booking,
            EventFields.MAX_SEATS_PER_BOOKING: event.max_seats_per_booking,
        }

        try:
            validate_event_dates(attrs, instance=event)
        except serializers.ValidationError as exc:
            for field, err in exc.detail.items():
                msg = err[0] if isinstance(err, list) else str(err)
                messages.error(request, msg)
            vendors = Vendor.objects.filter(is_active=True)
            return render(request, "dashboard/events/form.html", {"event": event, "vendors": vendors})

        event.save()

        messages.success(request, Messages.Event.UPDATED_TITLE_SUCCESS.format(title=event.title))
        return redirect("dashboard:event-list")


class EventToggleStatusView(StaffRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.is_active = not event.is_active
        event.save()
        status_label = "Active" if event.is_active else "Inactive"
        messages.success(request, Messages.Event.STATUS_UPDATED.format(title=event.title, status=status_label))
        return redirect("dashboard:event-list")


class EventDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        from apps.bookings.models import Booking
        event = get_object_or_404(Event.objects.select_related("vendor"), pk=pk)
        event_bookings = Booking.objects.filter(event=event).select_related("user").order_by("-created_at")

        context = {
            "event": event,
            "event_bookings": event_bookings,
        }
        return render(request, "dashboard/events/detail.html", context)


# ---------------------------------------------------------------------------
# Booking Views
# ---------------------------------------------------------------------------

class BookingListView(StaffRequiredMixin, View):
    def get(self, request):
        search = request.GET.get(FilterParams.SEARCH, "")
        status_filter = request.GET.get(BookingFields.FILTER_STATUS, "")
        qs = Booking.objects.select_related("user", "event").all()

        if search:
            qs = qs.filter(user__email__icontains=search) | qs.filter(event__title__icontains=search)

        if status_filter:
            qs = qs.filter(status__iexact=status_filter)

        return render(request, "dashboard/bookings/list.html", {"bookings": qs.order_by("-created_at")})


class BookingCancelView(StaffRequiredMixin, View):
    def post(self, request, pk):
        update_booking_status(booking_id=str(pk), new_status=BookingStatus.CANCELLED, requesting_user=request.user)
        messages.success(request, Messages.Booking.CANCELLED_RESTORED)
        return redirect("dashboard:booking-list")


class BookingStatusUpdateView(StaffRequiredMixin, View):
    def post(self, request, pk):
        new_status = request.POST.get("status")
        valid_statuses = [BookingStatus.CONFIRMED, BookingStatus.PENDING, BookingStatus.CANCELLED, BookingStatus.FAILED]
        if new_status in valid_statuses:
            update_booking_status(booking_id=str(pk), new_status=new_status, requesting_user=request.user)
            messages.success(request, Messages.Booking.STATUS_UPDATED.format(status=new_status.upper()))
        else:
            messages.error(request, Messages.Booking.STATUS_INVALID)
        return redirect("dashboard:booking-list")


class BookingDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        booking = get_object_or_404(
            Booking.objects.select_related("user", "event", "event__vendor"),
            pk=pk,
        )
        return render(request, "dashboard/bookings/detail.html", {"booking": booking})


# ---------------------------------------------------------------------------
# User Views
# ---------------------------------------------------------------------------

class UserListView(StaffRequiredMixin, View):
    def get(self, request):
        search = request.GET.get(FilterParams.SEARCH, "")
        role_filter = request.GET.get("role", "")
        qs = User.objects.all()

        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(referral_code__icontains=search)

        if role_filter == "staff":
            qs = qs.filter(is_staff=True)
        elif role_filter == "customer":
            qs = qs.filter(is_staff=False)

        return render(request, "dashboard/users/list.html", {"users": qs.order_by(CommonFields.UPDATED_AT_DESC)})


class UserDetailView(StaffRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        from apps.referrals.selectors import build_tree_dict, get_referral_node, get_referral_stats

        node = get_referral_node(str(user.id))
        tree_dict = build_tree_dict(node) if node else None
        stats = get_referral_stats(node) if node else None

        user_bookings = Booking.objects.filter(user=user).select_related("event")

        context = {
            "target_user": user,
            "tree_dict": tree_dict,
            "stats": stats,
            "user_bookings": user_bookings,
        }
        return render(request, "dashboard/users/detail.html", context)


class UserToggleStaffView(StaffRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, Messages.User.CANNOT_MODIFY_SELF)
            return redirect("dashboard:user-list")
        user.is_staff = not user.is_staff
        user.save()
        role_label = "Staff" if user.is_staff else "Customer"
        messages.success(request, Messages.User.STATUS_UPDATED.format(email=user.email, role=role_label))
        return redirect("dashboard:user-list")


