from typing import Optional

from apps.core.constants import CommonFields, StatusChoices
from apps.vendors.models import Vendor


def get_all_vendors(name: str | None = None, status: str | None = None):

    qs = Vendor.objects.all()

    if name:
        qs = qs.filter(company_name__icontains=name)

    if status == StatusChoices.ACTIVE:
        qs = qs.filter(is_active=True)
    elif status == StatusChoices.INACTIVE:
        qs = qs.filter(is_active=False)

    return qs.order_by(CommonFields.UPDATED_AT_DESC)



def get_active_vendors():
    return Vendor.objects.filter(is_active=True).order_by(CommonFields.UPDATED_AT_DESC)



def get_vendor_by_id(vendor_id: str) -> Optional[Vendor]:
    try:
        return Vendor.objects.get(id=vendor_id)
    except Vendor.DoesNotExist:
        return None


def vendor_exists_by_email(email: str, exclude_id: str | None = None) -> bool:
    qs = Vendor.objects.filter(contact_email__iexact=email)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


def get_vendor_active_events_count(vendor_id: str) -> int:
    from apps.events.models import Event

    return Event.objects.filter(vendor_id=vendor_id, is_active=True).count()

