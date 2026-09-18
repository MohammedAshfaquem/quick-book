from rest_framework import serializers

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
        ]

    def validate_contact_email(self, value):
        qs = Vendor.objects.filter(contact_email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A vendor with this email already exists.")
        return value


class VendorStatusSerializer(serializers.Serializer):

    is_active = serializers.BooleanField()
