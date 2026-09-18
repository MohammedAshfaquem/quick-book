from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.authentication.constants import JWTFields, UserFields
from apps.authentication.models import User
from apps.core.errors import Errors
from apps.core.exceptions import QuickBookException


def get_tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        JWTFields.ACCESS: str(refresh.access_token),
        JWTFields.REFRESH: str(refresh),
    }


def register_user(validated_data: dict) -> tuple[User, dict]:
    referral_code_input = validated_data.pop(UserFields.REFERRAL_CODE, None)
    referring_user = None

    if referral_code_input:
        try:
            referring_user = User.objects.get(referral_code=referral_code_input)
        except User.DoesNotExist:
            raise QuickBookException(Errors.Auth.REFERRAL_CODE_NOT_FOUND)

        # Referral code valid but referrer account is deactivated
        if not referring_user.is_active:
            raise QuickBookException(Errors.Auth.REFERRER_INACTIVE)

    email = validated_data[UserFields.EMAIL]
    username = validated_data.get(UserFields.USERNAME) or email
    is_staff = validated_data.get(UserFields.IS_STAFF, False)

    # create_user handles password hashing automatically
    user = User.objects.create_user(
        email=email,
        username=username,
        password=validated_data[UserFields.PASSWORD],
        first_name=validated_data.get(UserFields.FIRST_NAME, ""),
        last_name=validated_data.get(UserFields.LAST_NAME, ""),
        is_staff=is_staff,
        referred_by=referring_user,
    )

    if referring_user:
        from apps.referrals.services import place_user_in_referral_tree
        place_user_in_referral_tree(user, referring_user)

    tokens = get_tokens_for_user(user)
    return user, tokens


def login_user(email: str, password: str) -> tuple[User, dict]:
    user = authenticate(username=email, password=password)

    if user is None:
        raise QuickBookException(Errors.Auth.INVALID_CREDENTIALS)

    if not user.is_active:
        raise QuickBookException(Errors.Auth.ACCOUNT_DEACTIVATED)

    tokens = get_tokens_for_user(user)
    return user, tokens


def logout_user(refresh_token: str) -> None:
    token = RefreshToken(refresh_token)
    token.blacklist()
