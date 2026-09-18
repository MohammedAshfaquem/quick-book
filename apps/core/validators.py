from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r"^\+?[0-9]{7,15}$",
    message="Enter a valid phone number (7 to 15 digits, optional '+' country code prefix).",
)
