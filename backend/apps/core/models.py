from django.db import models


class BaseMixinModel(models.Model):
    class Meta:
        abstract = True
        default_related_name = '%(app_label)s_%(class)s'


class TimeStampModel(models.Model):
    """Абстрактаня модель для временных меток."""

    created_at = models.DateTimeField(
        'создано', auto_now_add=True, help_text='Дата и время создания записи'
    )
    updated_at = models.DateTimeField(
        'обновлено',
        auto_now=True,
        help_text='Дата и время последнего изменения записи',
    )

    class Meta:
        abstract = True
        ordering = ('-updated_at', '-created_at')
