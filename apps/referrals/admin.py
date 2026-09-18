from django.contrib import admin

from apps.referrals.models import ReferralNode


@admin.register(ReferralNode)
class ReferralNodeAdmin(admin.ModelAdmin):
    """Admin view for the ReferralNode model."""

    list_display = ["user", "parent", "left_child", "right_child", "created_at", "updated_at"]
    search_fields = ["user__email", "user__referral_code"]
    readonly_fields = ["id", "created_at", "updated_at"]
