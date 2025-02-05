from django.db import models

from . import constants


class Tag(models.Model):
    """Модель для описания тега"""

    name = models.CharField(
        max_length=constants.NAME_MAX_LENGH,
        unique=True,
        verbose_name='Название тэга')

    slug = models.SlugField(
        max_length=constants.SLUG_MAX_LENGH,
        unique=True,
        verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug'),
                name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name
