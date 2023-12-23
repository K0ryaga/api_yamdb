from django.core.validators import validate_slug
from django.core.exceptions import ValidationError


def not_me_username_validator(value):
    if value == "me":
        raise ValidationError("Имя пользователя 'me' запрещено.")


def username_validator(value):
    validate_slug(value)
