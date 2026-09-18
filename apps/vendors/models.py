from django.db import models

from apps.core.constants import CommonFields, VerboseNames
from apps.core.mixins import BaseModel
from apps.core.validators import phone_number_validator
from apps.vendors.constants import VendorFields


class Vendor(BaseModel):
    company_name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        validators=[phone_number_validator],
    )
    description = models.TextField(blank=True, default="")
    logo_url = models.URLField(blank=True,default="")

    class Meta:
        verbose_name = VerboseNames.Vendor.NAME
        verbose_name_plural = VerboseNames.Vendor.PLURAL
        ordering = [CommonFields.UPDATED_AT_DESC]

    def __str__(self) -> str:
        return self.company_name
