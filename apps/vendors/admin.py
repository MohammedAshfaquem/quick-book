"""
Vendor admin — registers Vendor model with Django Admin.
"""

from django.contrib import admin

from apps.core.constants import CommonFields
from apps.vendors.constants import VendorFields
from apps.vendors.models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):

    list_display = [
        CommonFields.ID,
        VendorFields.COMPANY_NAME,
        VendorFields.CONTACT_EMAIL,
        VendorFields.CONTACT_PHONE,
        VendorFields.IS_ACTIVE,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
    list_filter = [VendorFields.IS_ACTIVE]
    search_fields = [VendorFields.COMPANY_NAME, VendorFields.CONTACT_EMAIL]
    ordering = [CommonFields.UPDATED_AT_DESC]
    readonly_fields = [
        CommonFields.ID,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
