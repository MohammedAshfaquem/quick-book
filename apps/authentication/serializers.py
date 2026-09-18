from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.authentication.constants import JWTFields, UserFields
from apps.authentication.models import User
from apps.core.constants import CommonFields
from apps.core.messages import Messages


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    is_staff = serializers.BooleanField(required=False, default=False)
    referral_code = serializers.CharField(max_length=10, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            UserFields.EMAIL,
            UserFields.USERNAME,
            UserFields.FIRST_NAME,
            UserFields.LAST_NAME,
            UserFields.PASSWORD,
            UserFields.PASSWORD_CONFIRM,
            UserFields.IS_STAFF,
            UserFields.REFERRAL_CODE,
        ]

    def validate(self, attrs):
        if attrs[UserFields.PASSWORD] != attrs.pop(UserFields.PASSWORD_CONFIRM):
            raise serializers.ValidationError({UserFields.PASSWORD: Messages.Auth.PASSWORDS_DO_NOT_MATCH})
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            CommonFields.ID,
            UserFields.EMAIL,
            UserFields.USERNAME,
            UserFields.FIRST_NAME,
            UserFields.LAST_NAME,
            UserFields.REFERRAL_CODE,
            UserFields.IS_STAFF,
            UserFields.DATE_JOINED,
            CommonFields.CREATED_AT,
        ]
        read_only_fields = fields


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="JWT refresh token to blacklist.")
