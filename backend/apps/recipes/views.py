from django.shortcuts import get_object_or_404, redirect

from apps.recipes.models import Recipe


def redirect_to_recipe(request, short_code):
    """Перенаправляет c короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_code=short_code)
    return redirect(f'/recipes/{recipe.id}/')
