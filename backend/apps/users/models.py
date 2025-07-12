from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Пользовательская модель пользователя, расширяющая AbstractUser."""

    # class Meta:
    #     verbose_name = 'пользователь'
    #     verbose_name_plural = 'пользователи'
