from django.core.mail import send_mail

from foodgram_backend import settings


def sending_mail(user):
    send_mail(
        'Ваш код подтверждения',
        f'Ваш код подтверждения: {user.confirmation_code}',
        f'{settings.DEFAULT_FROM_EMAIL}',
        [f'{user.email}']
    )
    return True
