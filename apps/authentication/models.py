import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.authentication.constants import UserFields
from apps.core.constants import CommonFields, VerboseNames
from apps.core.mixins import TimeStampMixin


class User(TimeStampMixin, AbstractUser):
    email = models.EmailField(unique=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)
    referred_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=UserFields.RELATION_REFERRALS,
    )

    USERNAME_FIELD = UserFields.EMAIL
    REQUIRED_FIELDS = [UserFields.USERNAME]

    class Meta(AbstractUser.Meta):
        ordering = [CommonFields.UPDATED_AT_DESC]
        verbose_name = VerboseNames.User.NAME
        verbose_name_plural = VerboseNames.User.PLURAL

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_referral_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_referral_code() -> str:
        return uuid.uuid4().hex[:8].upper()
