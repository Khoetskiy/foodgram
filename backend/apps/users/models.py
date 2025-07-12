from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Пользовательская модель пользователя, расширяющая AbstractUser."""
