from django.core.validators import RegexValidator
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

VALIDATOR_REGEX = RegexValidator(r'^[\w.@+-]+\Z')
VALIDATOR_ME = RegexValidator(r'[^m][^e]')

def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            (f'Указанный год {value} больше текущего {now}')
        )
    return value


def validate_username(username):
    pattern = re.compile(r'[\w.@+-]+')
    invalid_chars = pattern.sub('', username)
    if invalid_chars:
        raise ValidationError(
            f'Некорректные символы в username: {invalid_chars}'
        )
    if username == settings.FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Username "{settings.FORBIDDEN_USERNAME}"'
            f' нельзя регистрировать!'
        )
    return username
