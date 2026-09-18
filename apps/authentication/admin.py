
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.authentication.constants import UserFields
from apps.authentication.models import User
from apps.core.constants import CommonFields


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin view for the User model using domain constants."""

    list_display = [
        UserFields.EMAIL,
        UserFields.USERNAME,
        UserFields.REFERRAL_CODE,
        UserFields.IS_STAFF,
        CommonFields.IS_ACTIVE,
        UserFields.DATE_JOINED,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
    list_filter = [UserFields.IS_STAFF, CommonFields.IS_ACTIVE]
    search_fields = [UserFields.EMAIL, UserFields.USERNAME, UserFields.REFERRAL_CODE]
    ordering = [CommonFields.UPDATED_AT_DESC]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "QuickBook Fields",
            {
                "fields": (UserFields.REFERRAL_CODE, UserFields.REFERRED_BY),
            },
        ),
    )

    readonly_fields = [
        UserFields.REFERRAL_CODE,
        UserFields.DATE_JOINED,
        CommonFields.CREATED_AT,
        CommonFields.UPDATED_AT,
    ]
