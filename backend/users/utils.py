import random
import re

from django.core.exceptions import ValidationError


def code_random():
    return random.randint(1000, 10000)


def validate_username(username):
    if username == 'me':
        raise ValidationError('Нельзя использовать имя me.')
    elif not re.match(r'^[\w.@+-]+\Z', username):
        raise ValidationError(
            'Введите валидное имя. Поле может содержать только буквы,'
            'цифры и @/./+/-/_ данные симмволы.'
        )
    return username
