# ruff: noqa: RUF012 RUF002
from django.contrib.auth.models import AbstractUser
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
    CUSTOMUSER_AVATAR_HELP,
    CUSTOMUSER_EMAIL_HELP,
    CUSTOMUSER_FIRSTNAME_HELP,
    CUSTOMUSER_LASTNAME_HELP,
    CUSTOMUSER_USERNAME_HELP,
    EMAIL_LENGTH,
    FAVORITE_USER_HELP,
    FAVORITEITEM_FAVORITE_HELP,
    FAVORITEITEM_RECIPE_HELP,
    FIRST_NAME_LENGTH,
    FIRST_NAME_MIN_LENGTH,
    LAST_NAME_LENGTH,
    LAST_NAME_MIN_LENGTH,
    NAME_VALIDATION_REGEX,
    SUBSCRIBE_AUTHOR_HELP,
    SUBSCRIBE_USER_HELP,
    USERNAME_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_VALIDATION_REGEX,
)
from apps.core.models import TimeStampModel
from apps.core.utils import capitalize_name
from apps.core.validators import validate_file_size, validate_safe_filename


class CustomUser(AbstractUser):
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

    username = models.CharField(
        'имя пользователя',
        max_length=USERNAME_LENGTH,
        unique=True,
        help_text=CUSTOMUSER_USERNAME_HELP,
        validators=[
            MinLengthValidator(
                USERNAME_MIN_LENGTH,
                message=(
                    'Имя пользователя не может быть короче '
                    f'{USERNAME_MIN_LENGTH} символов(а)'
                ),
            ),
            RegexValidator(
                regex=USERNAME_VALIDATION_REGEX,
                message=(
                    'Имя пользователя может содержать только '
                    'латинские буквы, цифры и подчёркивания.'
                ),
            ),
        ],
    )
    email = models.EmailField(
        'электронная почта',
        max_length=EMAIL_LENGTH,
        help_text=CUSTOMUSER_EMAIL_HELP,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        help_text=CUSTOMUSER_FIRSTNAME_HELP,
        max_length=FIRST_NAME_LENGTH,
        validators=[
            MinLengthValidator(
                FIRST_NAME_MIN_LENGTH,
                message=(
                    'Имя не может быть короче '
                    '{FIRST_NAME_MIN_LENGTH} символов(а)'
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
        help_text=CUSTOMUSER_LASTNAME_HELP,
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
        upload_to='avatars/',  # TODO: Сделать загрузку как c фото рецептами?
        blank=True,
        null=True,
        help_text=CUSTOMUSER_AVATAR_HELP,
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
        # TODO: Добавить поддержку двойных имен и фамилий через regex
        self.first_name = capitalize_name(self.first_name)
        self.last_name = capitalize_name(self.last_name)
        if self.first_name.lower() == self.last_name.lower():
            msg = 'Имя и фамилия не должны совпадать.'
            raise ValidationError(msg, code='name_match')
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Favorite(TimeStampModel):
    """
    Модель списка избранного пользователя.
    У каждого пользователя может быть только один список избранного.


    Attributes:
        user (CustomUser): Пользователь, которому принадлежит список избранного
    """

    user = models.OneToOneField(
        CustomUser,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        help_text=FAVORITE_USER_HELP,
        related_name='favorite',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'избранные'
        indexes = [models.Index(fields=['user'], name='favorite_user_idx')]

    def __str__(self) -> str:
        return f'Избранное пользователя: {str(self.user.username).upper()}'


class Favoriteitem(TimeStampModel):
    """
    Элемент избранного: связь между избранным и рецептом.

    Один FavoriteItem связывает один Favorite c одним Recipe.

    Attributes:
        favorite (Favorite): Избранное, к которому относится этот элемент.
        recipe (Recipe): Рецепт, добавленный в избранное.
    """

    favorite = models.ForeignKey(
        Favorite,
        verbose_name='избранное',
        on_delete=models.CASCADE,
        help_text=FAVORITEITEM_FAVORITE_HELP,
        related_name='items',
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        help_text=FAVORITEITEM_RECIPE_HELP,
        related_name='favorited_by',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'элемент избранного'
        verbose_name_plural = 'элементы избранного'
        constraints = [
            models.UniqueConstraint(
                fields=['favorite', 'recipe'], name='unique_favorite_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в избранном {self.favorite.user.username}'


class Subscribe(TimeStampModel):
    """
    Модель подписок между пользователями.

    Attributes:
        user (CustomUser): Кто подписывается.
        author (CustomUser): На кого подписываются.
    """

    user = models.ForeignKey(
        CustomUser,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        help_text=SUBSCRIBE_USER_HELP,
        related_name='subscriptions',
    )
    author = models.ForeignKey(
        CustomUser,
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
