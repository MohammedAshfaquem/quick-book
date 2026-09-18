from rest_framework import serializers

from apps.core.messages import Messages
from apps.vendors.models import Vendor


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = [
            "id",
            "company_name",
            "contact_email",
            "contact_phone",
            "description",
            "logo_url",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VendorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "company_name",
            "contact_email",
            "contact_phone",
            "description",
            "logo_url",
        ]

    def validate_contact_email(self, value):
        qs = Vendor.objects.filter(contact_email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(Messages.Vendor.EMAIL_EXISTS.format(email=value))
        return value


class VendorStatusSerializer(serializers.Serializer):

    is_active = serializers.BooleanField()
