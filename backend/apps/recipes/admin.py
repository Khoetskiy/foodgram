from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count

from apps.core.admin_mixins import ReadOnlyInLineMixin
from apps.core.constants import TEXT_TRUNCATE_LENGTH_ADMIN
from apps.core.services import get_objects
from apps.core.utils import format_duration_time, truncate_text
from apps.recipes.models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeIngredient,
    Tag,
)

User = get_user_model()


class IngredientInLine(ReadOnlyInLineMixin, admin.TabularInline):
    """Inline-форма для модели Ingredient, используемая в админке."""

    model = Ingredient
    extra = 0
    fields = ('name', 'created_at')
    readonly_fields = ('name', 'created_at')
    verbose_name = 'ингредиент'
    verbose_name_plural = 'связанные ингредиенты'
    ordering = ('-created_at',)


class IngredientRecipeInLine(admin.TabularInline):
    """Inline-форма для отображения Ingredient в админке модели Recipe."""

    model = RecipeIngredient
    extra = 0
    fields = ('ingredient', 'amount', 'get_measurement_unit')
    readonly_fields = ('get_measurement_unit',)
    autocomplete_fields = ('ingredient',)
    min_num = 1
    show_change_link = True
    ordering = ('created_at',)
    verbose_name = 'ингредиент'
    verbose_name_plural = 'список ингредиентов'

    @admin.display(description='Ед. изм.')
    def get_measurement_unit(self, obj):
        """Показывает единицу измерения, связанную c ингредиентом."""
        if obj.ingredient_id:
            return obj.ingredient.measurement_unit.name
        return '-'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recipe', 'ingredient__measurement_unit')


class RecipeIngredientInLine(ReadOnlyInLineMixin, admin.TabularInline):
    """Inline-форма для отображения Recipe в админке модели Ingredient."""

    model = RecipeIngredient
    extra = 0
    fields = ('recipe',)
    verbose_name = 'рецепт'
    verbose_name_plural = 'связанные рецепты'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recipe', 'ingredient')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ-класс для модели Tag."""

    list_display = ('name', 'slug', 'updated_at', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('updated_at', 'created_at')
    fieldsets = (
        (None, {'fields': ('name', 'slug')}),
        (
            'Системная информация',
            {
                'fields': ('updated_at', 'created_at'),
                'classes': ('extrapretty',),
            },
        ),
    )
    readonly_fields = ('updated_at', 'created_at')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Ingredient.

    Включает:
        - встроенный RecipeIngredientInLine для рецептов;
    """

    inlines = (RecipeIngredientInLine,)
    list_display = ('name', 'measurement_unit', 'updated_at', 'created_at')
    search_fields = ('name', 'measurement_unit__name')
    autocomplete_fields = ('measurement_unit',)
    list_filter = ('updated_at', 'created_at')
    fieldsets = (
        (None, {'fields': ('name', 'measurement_unit')}),
        (
            'Системная информация',
            {
                'fields': ('updated_at', 'created_at'),
                'classes': ('extrapretty',),
            },
        ),
    )
    readonly_fields = ('updated_at', 'created_at')


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели MeasurementUnit.

    Включает:
        - встроенный IngredientInLine для ингредиентов;
    """

    inlines = (IngredientInLine,)
    list_display = ('name', 'updated_at', 'created_at')
    search_fields = ('name',)
    list_filter = ('updated_at', 'created_at')
    fieldsets = (
        (None, {'fields': ('name',)}),
        (
            'Системная информация',
            {
                'fields': ('updated_at', 'created_at'),
                'classes': ('extrapretty',),
            },
        ),
    )
    readonly_fields = ('updated_at', 'created_at')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Recipe.

    Включает:
        - кастомные отображения названия, описания, ингредиентов
                                        и времени приготовления;
        - встроенный IngredientRecipeInLine для ингредиентов;
        - аннотацию количества добавлений в избранное.
    """

    inlines = (IngredientRecipeInLine,)
    list_display = (
        'short_name',
        'author',
        'short_text',
        'get_ingredients',
        'cooking_time_display',
        'is_favorited',
        'image',
        'updated_at',
        'created_at',
    )
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'updated_at', 'created_at')
    autocomplete_fields = ('author',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'name',
                    'author',
                    'text',
                    'image',
                    'cooking_time',
                    'tags',
                )
            },
        ),
        (
            'Системная информация',
            {
                'fields': ('created_at', 'updated_at'),
                'classes': ('extrapretty',),
            },
        ),
    )

    @admin.display(description='название')
    def short_name(self, obj):
        """Возвращает сокращенное название рецепта."""
        return truncate_text(obj.name, length=TEXT_TRUNCATE_LENGTH_ADMIN)

    @admin.display(description='описание')
    def short_text(self, obj):
        """Возвращает сокращенное описание рецепта."""
        return truncate_text(obj.text, length=TEXT_TRUNCATE_LENGTH_ADMIN)

    @admin.display(description='время приготовления')
    def cooking_time_display(self, obj):
        """Возвращает человекочитаемое время приготовления."""
        return format_duration_time(obj.cooking_time)

    @admin.display(description='В избранном (раз)')
    def is_favorited(self, obj):
        """Возвращает кол.-во. пользователей, добавивших рецепт в избранное."""
        return obj.fav_count

    @admin.display(description='ингредиенты')
    def get_ingredients(self, obj):
        """Возвращает связанные ингредиенты, в виде списка HTML-блока."""
        return get_objects(
            items=obj.ingredients.all(),
            admin_url='admin:recipes_ingredient_change',
            item_args=lambda item: [item.id],
            display_value=lambda item: item.name,
            title='Показать ингредиенты',
        )

    def get_queryset(self, request):
        """
        Расширяет queryset:
            - добавляет prefetch_related для ингредиентов;
            - аннотирует количество добавлений в избранное.
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('ingredients').annotate(
            fav_count=Count('favorites')
        )
