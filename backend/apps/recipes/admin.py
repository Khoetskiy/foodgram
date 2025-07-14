from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.recipes.models import Ingredient, MeasurementUnit, Tag

User = get_user_model()


# TODO: Скорее всего убрать, тк не нужно, сделать для других связей.
class IngredientInLine(admin.StackedInline):
    """Inline-форма для модели Ingredient, используемая в админке."""

    model = Ingredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    # TODO: Настроить регистронезависимый поиск по названию (вхождение в начало, опционально — в произвольном месте).


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    inlines = (IngredientInLine,)
    list_display = ('id', 'name')
    search_fields = ('id', 'name')
