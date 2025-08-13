
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.recipes'
    verbose_name = 'рецепты'

    def ready(self):
        import apps.recipes.signals  # noqa:F401
