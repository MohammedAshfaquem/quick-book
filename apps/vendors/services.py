from typing import Any
from apps.core.constants import ActionType, CommonFields
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException
from apps.core.messages import Messages
from apps.vendors.constants import VendorFields
from apps.vendors.models import Vendor
from apps.vendors.selectors import (
    get_vendor_by_id,
    get_vendor_active_events_count,
    vendor_exists_by_email,
)


def create_vendor(
    validated_data: dict,
    action: str = ActionType.CONFIRM,
) -> Vendor | dict[str, Any]:

    if vendor_exists_by_email(validated_data[VendorFields.CONTACT_EMAIL]):
        raise QuickBookException(Errors.Vendor.ALREADY_EXISTS)

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Vendor.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }

    elif action == ActionType.CONFIRM:
        return Vendor.objects.create(**validated_data)

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)



def update_vendor(
    vendor_id: str,
    validated_data: dict,
    action: str = ActionType.CONFIRM,
) -> Vendor | dict[str, Any]:

    vendor = get_vendor_by_id(vendor_id)

    if vendor is None:
        raise QuickBookException(Errors.Vendor.NOT_FOUND)

    email = validated_data.get(VendorFields.CONTACT_EMAIL)
    if email and vendor_exists_by_email(email, exclude_id=vendor_id):
        raise QuickBookException(Errors.Vendor.ALREADY_EXISTS)

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Vendor.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }

    elif action == ActionType.WARNING:
        active_events_count = get_vendor_active_events_count(vendor_id)
        has_warning = active_events_count > 0
        warning_msg = (
            f"Updating vendor '{vendor.company_name}' will affect {active_events_count} active event(s)."
            if has_warning
            else ""
        )

        return {
            "has_warning": has_warning,
            "warning_message": warning_msg,
            "action": ActionType.WARNING,
        }

    elif action == ActionType.CONFIRM:
        for field, value in validated_data.items():
            setattr(vendor, field, value)

        update_fields = list(validated_data.keys()) + [CommonFields.UPDATED_AT]
        vendor.save(update_fields=update_fields)
        return vendor

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)


def set_vendor_status(
    vendor_id: str,
    is_active: bool,
    action: str = ActionType.CONFIRM,
) -> Vendor | dict[str, Any]:

    vendor = get_vendor_by_id(vendor_id)

    if vendor is None:
        raise QuickBookException(Errors.Vendor.NOT_FOUND)

    if action == ActionType.SUBMIT:
        return {
            "message": Messages.Vendor.SUBMIT_SUCCESS,
            "action": ActionType.SUBMIT,
        }

    elif action == ActionType.WARNING:
        has_warning = False
        warning_msg = ""
        if not is_active:
            active_events_count = get_vendor_active_events_count(vendor_id)
            if active_events_count > 0:
                has_warning = True
                warning_msg = f"Deactivating '{vendor.company_name}' will affect {active_events_count} active event(s)."

        return {
            "has_warning": has_warning,
            "warning_message": warning_msg,
            "action": ActionType.WARNING,
        }

    elif action == ActionType.CONFIRM:
        vendor.is_active = is_active
        vendor.save(update_fields=[VendorFields.IS_ACTIVE, CommonFields.UPDATED_AT])
        return vendor

    else:
        raise QuickBookException(Errors.Params.INVALID_PARAMS)



