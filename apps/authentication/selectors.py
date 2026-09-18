from typing import Optional
from apps.authentication.constants import UserFields
from apps.authentication.models import User
from apps.core.constants import CommonFields, StatusChoices


def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def get_user_by_email(email: str) -> Optional[User]:
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def get_user_by_referral_code(referral_code: str) -> Optional[User]:
    try:
        return User.objects.get(referral_code=referral_code)
    except User.DoesNotExist:
        return None


def get_all_active_users():
    return User.objects.filter(**{UserFields.IS_ACTIVE: True, UserFields.IS_STAFF: False})


def get_all_users(status: str | None = None):
    qs = User.objects.all()

    if status == StatusChoices.ACTIVE:
        qs = qs.filter(is_active=True)
    elif status == StatusChoices.INACTIVE:
        qs = qs.filter(is_active=False)


    return qs.order_by(CommonFields.UPDATED_AT_DESC)


def user_exists_by_email(email: str) -> bool:
    return User.objects.filter(email=email).exists()
