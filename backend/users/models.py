from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import (
    LENGTH_CHARFIELDS,
    LENGTH_EMAIL,
    UNIQUE_EMAIL,
    UNIQUE_USERNAME,
)


class ApiUser(AbstractUser):
    username = models.CharField(
        'имя пользователя',
        max_length=LENGTH_CHARFIELDS,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z')
            ],
        unique=True,
        error_messages={
            'unique': (UNIQUE_USERNAME)
        }
    )
    email = models.EmailField(
        'почтовый адрес',
        max_length=LENGTH_EMAIL, unique=True,
        error_messages={
            'unique': (UNIQUE_EMAIL)
        }
    )
    first_name = models.CharField(
        'имя', max_length=LENGTH_CHARFIELDS, blank=False,
    )
    last_name = models.CharField(
        'фамилия', max_length=LENGTH_CHARFIELDS, blank=False
    )

    avatar = models.ImageField(
        upload_to='user/avatars/', null=True, blank=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс для подписки на авторов контента."""

    subscriber = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'subscriber'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('subscriber')),
                name='cannot_subscribe_to_self'
            ),
        )

    def __str__(self):
        return f'{self.subscriber} подписан на: {self.author}'
