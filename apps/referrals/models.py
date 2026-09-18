from django.db import models
from apps.authentication.models import User
from apps.core.constants import VerboseNames
from apps.core.mixins import BaseModel
from apps.referrals.constants import ReferralNodeFields


class ReferralNode(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name=ReferralNodeFields.RELATION_REFERRAL_NODE,
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=ReferralNodeFields.RELATION_CHILDREN,
    )
    left_child = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=ReferralNodeFields.RELATION_LEFT_PARENT,
    )
    right_child = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name=ReferralNodeFields.RELATION_RIGHT_PARENT,
    )

    class Meta:
        verbose_name = VerboseNames.ReferralNode.NAME
        verbose_name_plural = VerboseNames.ReferralNode.PLURAL

    def __str__(self) -> str:
        """Return user email."""
        return f"Node ({self.user.email})"
