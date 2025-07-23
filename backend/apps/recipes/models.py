from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Q

from apps.core.constants import (
    ALLOWED_EXTENSIONS,
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENT_NAME_MIN_LENGTH,
    MAX_COOK_TIME,
    MEASUREMENTUNIT_MAX_NAME_LENGTH,
    MIN_AMOUNT_INGREDIENTS,
    MIN_COOK_TIME,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from apps.core.exceptions import SlugGenerationError
from apps.core.models import TimeStampModel
from apps.core.utils import truncate_text
from apps.core.validators import (
    validate_file_size,
    validate_safe_filename,
)
from apps.recipes.services import (
    generate_unique_slug,
    recipe_image_upload_path,
)

User = get_user_model()


class MeasurementUnit(TimeStampModel):
    """
    Модель для хранения единиц измерения ингредиентов.

    Attributes:
        name (str): Единица измерения для ингредиентов

    """

    name = models.CharField(
        'название',
        max_length=MEASUREMENTUNIT_MAX_NAME_LENGTH,
        unique=True,
        help_text='Единица измерения (г, мл, шт и т.д.).',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'единица измерения'
        verbose_name_plural = 'единицы измерения'
        ordering = ('name',)

    def __str__(self) -> str:
        return truncate_text(self.name)

    def clean(self):
        """Валидирует поле name, проверяя корректность данных."""
        if not self.name:
            raise ValidationError(
                {'name': 'Единица измерения не может быть пустой.'}
            )
        self.name = self.name.strip().lower()
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Ingredient(TimeStampModel):
    """
    Модель для хранения ингредиентов c их единицами измерения.

    Attributes:
        name (str): Название ингредиента.
        measurement_unit (MeasurementUnit): Связанная единица измерения.
    """

    name = models.CharField(
        'название',
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
        validators=[
            MinLengthValidator(
                INGREDIENT_NAME_MIN_LENGTH,
                message=(
                    'Название ингредиента должно содержать '
                    f'минимум {INGREDIENT_NAME_MIN_LENGTH} символа(ов).'
                ),
            )
        ],
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name='единица измерения',
        on_delete=models.PROTECT,
        related_name='ingredients',
        help_text='Выберите единицу измерения для ингредиента.',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)

    def __str__(self) -> str:
        return truncate_text(self.name)

    def clean(self):
        """Валидирует поля модели, проверяя корректность данных."""
        if not self.name:
            raise ValidationError(
                {'name': 'Название ингредиента не может быть пустым.'}
            )
        self.name = self.name.strip().lower()
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Tag(TimeStampModel):
    """
    Модель для хранения тегов для рецептов.

    Attributes:
        name (str): Название тега.
        slug (str): Уникальный URL-дружественный идентификатор тега.
    """

    name = models.CharField(
        'название',
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        help_text='Уникальное название тега для рецептов.',
    )
    slug = models.SlugField(
        'идентификатор',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        blank=True,
        help_text='Уникальный URL-дружественный идентификатор тега.',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ('name',)
        default_related_name = 'tags'

    def __str__(self) -> str:
        """Возвращает усеченное название тега."""
        return truncate_text(self.name)

    def clean(self):
        try:
            if (
                not self.slug
                or self.name != Tag.objects.only('name').get(pk=self.pk).name
            ):
                self.slug = generate_unique_slug(Tag, self.name, self)
        except Tag.DoesNotExist:
            if self.slug:  # Если пользователь сам заполнил slug
                return
            self.slug = generate_unique_slug(Tag, self.name, self)
        except (SlugGenerationError, RuntimeError) as e:
            raise ValidationError(
                {
                    'slug': (
                        'Не удалось автоматически сгенерировать слаг.'
                        ' Укажите его вручную.'
                    )
                }
            ) from e
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Recipe(TimeStampModel):
    """
    Модель рецепта c автором, ингредиентами, тегами, фото и временем готовки.

    Attributes:
        name (str): Название рецепта.
        author (User): Автор рецепта, связанный c User.
        text (str): Описание рецепта.
        tags (ManyToManyField): Теги, связанные c рецептом.
        ingredients (ManyToManyField): Ингредиенты рецепта.
        image (ImageField): Фотография готового блюда.
        cooking_time (int): Время приготовления рецепта в минутах.
    """

    name = models.CharField(
        'название',
        max_length=RECIPE_NAME_MAX_LENGTH,
        help_text=f'Название рецепта (до {RECIPE_NAME_MAX_LENGTH} символов)',
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.PROTECT,  # QUESTION: поменять поведение?
        help_text='Автор рецепта',
    )
    text = models.TextField('описание', help_text='Описание рецепта')
    tags = models.ManyToManyField(
        Tag, verbose_name='теги', help_text='Теги рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        help_text='Ингредиенты рецепта',
    )
    image = models.ImageField(
        'фото',
        upload_to=recipe_image_upload_path,
        help_text='Фотография готового блюда',
        validators=[
            FileExtensionValidator(
                ALLOWED_EXTENSIONS,
                'Недопустимое расширение файла. '
                f'Разрешены: {", ".join(ALLOWED_EXTENSIONS)}',
            ),
            validate_safe_filename,
            validate_file_size,
        ],
    )  # TODO: Картинка должна быть закодированная в Base64 на API
    cooking_time = models.PositiveIntegerField(
        'время приготовления',
        help_text='Время приготовления в минутах',
        validators=[
            MinValueValidator(
                MIN_COOK_TIME, f'Минимальное время: {MIN_COOK_TIME} мин'
            ),
            MaxValueValidator(
                MAX_COOK_TIME, f'Максимальное время: {MAX_COOK_TIME} мин'
            ),
        ],
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        default_related_name = 'recipes'
        indexes = [  # noqa: RUF012
            models.Index(fields=['name'], name='recipe_name_idx'),
            models.Index(fields=['author'], name='recipe_author_idx'),
        ]
        constraints = [  # noqa: RUF012
            models.CheckConstraint(
                check=Q(cooking_time__gte=MIN_COOK_TIME)
                & Q(cooking_time__lte=MAX_COOK_TIME),
                name='cooktime_range',
            ),
            models.UniqueConstraint(
                fields=['name', 'author'], name='unique_name_author'
            ),
        ]

    def __str__(self) -> str:
        return truncate_text(self.name)


class RecipeIngredient(models.Model):
    """
    Промежуточная, для связи рецепта и ингредиентов + доп. поле `amount`.

    Attributes:
        recipe (Recipe): Ссылка на связанный рецепт.
        ingredient (Ingredient): Ссылка на связанный ингредиент.
        amount (int): Количество ингредиента в рецепте.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        help_text='Рецепт, к которому относится ингредиент.',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
        help_text='Ингредиент, используемый в рецепте.',
    )
    amount = models.PositiveIntegerField(
        'количество',
        help_text='Количество ингридиентов в рецепте',
        validators=[
            MinValueValidator(
                MIN_AMOUNT_INGREDIENTS,
                f'Количество должно быть больше {MIN_AMOUNT_INGREDIENTS}.',
            ),
        ],
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('amount',)

    def __str__(self) -> str:
        return self.recipe.name
