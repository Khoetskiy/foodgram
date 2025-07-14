from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.utils import generate_unique_slug, truncate_text

from config.constants import (
    MAX_INGREDIENT_LENGTH,
    MAX_MEASUREMENTUNIT_LENGTH,
    MAX_NAME_LENGTH,
    MAX_TAG_LENGTH,
    MIN_INGREDIENT_LENGTH,
)

User = get_user_model()


class MeasurementUnit(models.Model):
    """Модель для хранения единиц измерения ингредиентов."""

    name = models.CharField(
        'название',
        max_length=MAX_MEASUREMENTUNIT_LENGTH,
        unique=True,
        help_text='Единица измерения для ингредиентов (грамм, литр).',
    )

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'единицы измерения'
        ordering = ('name',)
        default_related_name = '%(app_label)s_%(class)s'

    def __str__(self) -> str:
        return truncate_text(self.name)

    def clean(self):
        """Валидирует поле name, проверяя корректность данных."""
        self.name = self.name.strip().lower()
        if not self.name:
            raise ValidationError(
                {'name': 'Единица измерения не может быть пустой.'}
            )
        super().clean()


class Ingredient(models.Model):
    """Модель для хранения ингредиентов c их единицами измерения."""

    name = models.CharField(
        'название',
        max_length=MAX_INGREDIENT_LENGTH,
        unique=True,
        help_text='Уникальное название ингредиента для рецептов.',
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name='единица измерения',
        on_delete=models.PROTECT,
        help_text='Выберите единицу измерения для ингредиента.',
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)
        default_related_name = '%(app_label)s_%(class)s'

    def __str__(self) -> str:
        return truncate_text(self.name)

    def clean(self):
        """Валидирует поля модели, проверяя корректность данных."""
        self.name = self.name.strip().lower()
        if not self.name:
            raise ValidationError(
                {'name': 'Название ингредиента не может быть пустым.'}
            )
        if len(self.name) < MIN_INGREDIENT_LENGTH:
            raise ValidationError(
                {
                    'name': (
                        'Название ингредиента должно содержать '
                        f'минимум {MIN_INGREDIENT_LENGTH} символа(ов).'
                    )
                }
            )
        if not self.measurement_unit:
            raise ValidationError(
                {'measurement_unit': 'Необходимо выбрать единицу измерения.'}
            )
        super().clean()


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(
        'название',
        max_length=MAX_TAG_LENGTH,
        unique=True,
        help_text='Уникальное название тега для рецептов.',
    )
    slug = models.SlugField(
        'идентификатор',
        max_length=MAX_TAG_LENGTH,
        unique=True,
        blank=True,
        help_text='Уникальный URL-дружественный идентификатор тега.',
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)
        default_related_name = '%(app_label)s_%(class)s'

    def __str__(self) -> str:
        """Возвращает усеченное название тега."""
        return truncate_text(self.name)


# FIXME: Доделать модель!
class Recipe(models.Model):
    """Модель рецепта c автором, ингредиентами, тегами и временем готовки."""

    name = models.CharField('название', max_length=MAX_NAME_LENGTH)
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,  # TODO: решить?
        help_text='Пользователь (В рецепте - автор рецепта)',
    )
    text = models.TextField('описание')
    tags = models.ManyToManyField(Tag, verbose_name='теги', through='')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        help_text='Список ингредиентов',
    )
    image = models.ImageField(
        'фото',
        upload_to='',
        height_field='',
        width_field='',
        max_length=1,
    )
    is_favorited = models.BooleanField(
        'в избранном', default=False, help_text='Находится ли в избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        'в списке покупок', default=False, help_text='Находится ли в корзине'
    )
    cooking_time = models.PositiveIntegerField(
        'время приготовления', help_text='Время приготовления (в минутах)'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('name', 'author')
        default_related_name = '%(app_label)s_%(class)s_related'
        default_query_name = '%(app_label)s_%(class)ss'
        indexes = (
            models.Index(fields=['name']),
            models.Index(fields=['author']),
        )

    def __str__(self) -> str:
        return truncate_text(self.name)


class RecipeIngredient(models.Model):
    """Промежуточная для связи рецепта и ингредиентов + доп. поле `amount`."""

    recipe = models.ForeignKey(
        Recipe, verbose_name='рецепт', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient, verbose_name='ингредиент', on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField('количество')
