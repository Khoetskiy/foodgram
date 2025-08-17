# ruff: noqa: RUF012 RUF002
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.db import models
from django.db.models import F, Q

from apps.core.constants import (
    ALLOWED_EXTENSIONS,
    EMAIL_LENGTH,
    FIRST_NAME_LENGTH,
    FIRST_NAME_MIN_LENGTH,
    LAST_NAME_LENGTH,
    LAST_NAME_MIN_LENGTH,
    NAME_VALIDATION_REGEX,
    SUBSCRIBE_AUTHOR_HELP,
    SUBSCRIBE_USER_HELP,
    USER_AVATAR_HELP,
    USER_EMAIL_HELP,
    USER_FIRSTNAME_HELP,
    USER_LASTNAME_HELP,
    USER_USERNAME_HELP,
    USERNAME_LENGTH,
    USERNAME_MIN_LENGTH,
)
from apps.core.models import TimeStampModel
from apps.core.services import get_upload_path
from apps.core.utils import capitalize_name, truncate_text
from apps.core.validators import validate_file_size, validate_safe_filename


class User(AbstractUser):
    """
    Кастомная модель пользователя, расширяющая AbstractUser.
    Использует email в качестве основного идентификатора (USERNAME_FIELD).
    Поля: username, email, first_name, last_name, avatar.
    Поддерживает нормализацию имени и фамилии перед сохранением.

    Attributes:
        username (str): Уникальное имя пользователя.
        email (str): Электронная почта, используемая для аутентификации.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        avatar (ImageField): Пользовательский аватар.
    """

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        'имя пользователя',
        max_length=USERNAME_LENGTH,
        unique=True,
        help_text=USER_USERNAME_HELP,
        validators=[
            MinLengthValidator(
                USERNAME_MIN_LENGTH,
                message=(
                    'Имя пользователя не может быть короче '
                    f'{USERNAME_MIN_LENGTH} символов(а)'
                ),
            ),
            username_validator,
        ],
    )
    email = models.EmailField(
        'электронная почта',
        max_length=EMAIL_LENGTH,
        help_text=USER_EMAIL_HELP,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        help_text=USER_FIRSTNAME_HELP,
        max_length=FIRST_NAME_LENGTH,
        validators=[
            MinLengthValidator(
                FIRST_NAME_MIN_LENGTH,
                message=(
                    'Имя не может быть короче '
                    f'{FIRST_NAME_MIN_LENGTH} символов(а)'
                ),
            ),
            RegexValidator(
                regex=NAME_VALIDATION_REGEX,
                message='Допускаются только буквы кириллицы или латиницы.',
            ),
        ],
    )
    last_name = models.CharField(
        'Фамилия',
        help_text=USER_LASTNAME_HELP,
        max_length=LAST_NAME_LENGTH,
        validators=[
            MinLengthValidator(
                LAST_NAME_MIN_LENGTH,
                message=(
                    'Фамилия не может быть короче '
                    '{LAST_NAME_MIN_LENGTH} символов(а)'
                ),
            ),
            RegexValidator(
                regex=NAME_VALIDATION_REGEX,
                message='Допускаются только буквы кириллицы или латиницы.',
            ),
        ],
    )
    avatar = models.ImageField(
        'аватар',
        upload_to=get_upload_path,
        blank=True,
        default='',
        help_text=USER_AVATAR_HELP,
        validators=[
            FileExtensionValidator(
                ALLOWED_EXTENSIONS,
                'Недопустимое расширение файла. '
                f'Разрешены: {", ".join(ALLOWED_EXTENSIONS)}',
            ),
            validate_safe_filename,
            validate_file_size,
        ],
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        indexes = [
            models.Index(fields=['first_name'], name='users_first_name_idx'),
            models.Index(fields=['last_name'], name='users_last_name_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=~Q(first_name='') & ~Q(last_name=''),
                name='first_last_name_not_empty',
            ),
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_username_email'
            ),
        ]

    def __str__(self) -> str:
        return self.username

    def clean(self):
        """
        Нормализация и дополнительная валидация полей.

        Приводит first_name и last_name к виду c заглавной первой буквой.
        Проверяет, что first_name и last_name не совпадают (без учёта регистра)
        """
        self.first_name = capitalize_name(self.first_name)
        self.last_name = capitalize_name(self.last_name)
        if self.first_name.lower() == self.last_name.lower():
            msg = 'Имя и фамилия не должны совпадать.'
            raise ValidationError(msg, code='name_match')
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Subscribe(TimeStampModel):
    """
    Модель подписок между пользователями.

    Attributes:
        user (User): Кто подписывается.
        author (User): На кого подписываются.
    """

    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        help_text=SUBSCRIBE_USER_HELP,
        related_name='subscriptions',
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор контента',
        on_delete=models.CASCADE,
        help_text=SUBSCRIBE_AUTHOR_HELP,
        related_name='subscribers',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~Q(user__exact=F('author')),
                name='prevent_self_subscribe',
            ),
        ]

    def clean(self):
        if self.user == self.author:
            msg = 'Нельзя подписаться на самого себя.'
            raise ValidationError(msg, code='prohibit_yourself')
        super().clean()

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'


class UserRecipeRelation(TimeStampModel):
    """
    Базовая модель для связи пользователя и рецепта.

    Attributes:
        user (User): Текущий пользователь.
        recipe (Recipe): Связанный рецепт.
    """

    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        help_text='Пользователь, связанный с рецептом.',
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        help_text='Рецепт, связанный с пользователем.',
    )

    class Meta(TimeStampModel.Meta):
        abstract = True
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique_user_recipe',
            )
        ]

    def __str__(self) -> str:
        return truncate_text(
            f'{self.recipe.name} → {self.user.username}'
        )  # FIXME: Какие отображение выбрать?


class Cart(UserRecipeRelation):
    """Модель корзины покупок пользователя."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
        default_related_name = 'carts'

    # def __str__(self) -> str:
    #     return f'{self.recipe} в корзине {self.user.username}'


class Favorite(UserRecipeRelation):
    """Модель для избранных рецептов пользователя."""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        default_related_name = 'favorites'

    # def __str__(self) -> str:
    #     return f'{self.recipe} в избранном {self.user.username}'
