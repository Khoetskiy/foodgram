# TODO: Вынести повторяющийся код в Mixin
# FIXME: Оптимизировась все запросы

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse

from apps.core.constants import TEXT_TRUNCATE_LENGTH_ADMIN
from apps.core.utils import (
    format_duration_time,
    render_html_list_block,
    truncate_text,
)
from apps.recipes.models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeIngredient,
    Tag,
)

User = get_user_model()


class IngredientInLine(admin.TabularInline):
    """Inline-форма для модели Ingredient, используемая в админке."""

    model = Ingredient
    extra = 0


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    autocomplete_fields = ('ingredient',)
    min_num = 1
    verbose_name = 'ингредиент'
    verbose_name_plural = 'ингредиенты'
    show_change_link = True


class IngredientRecipeInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    autocomplete_fields = ('recipe',)
    verbose_name = 'рецепт'
    verbose_name_plural = 'связанные рецепты'
    show_change_link = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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
    inlines = (IngredientRecipeInLine,)
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
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
    # TODO: Настроить регистронезависимый поиск по названию (вхождение в начало, опционально — в произвольном месте)  # noqa: E501


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(admin.ModelAdmin):
    inlines = (IngredientInLine,)
    list_display = ('name',)
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


# TODO: Доделать для рецептов
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # TODO: Создать доп. индексы в модели
    inlines = (RecipeIngredientInLine,)
    list_display = (
        'short_name',
        'author',
        'short_text',
        'get_ingredients',
        'image',
        'cooking_time_display',
        'is_favorited',
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

    # TODO: Короткие докстринги добавить
    @admin.display(description='название')
    def short_name(self, obj):
        return truncate_text(obj.name, length=TEXT_TRUNCATE_LENGTH_ADMIN)

    @admin.display(description='описание')
    def short_text(self, obj):
        return truncate_text(obj.text, length=TEXT_TRUNCATE_LENGTH_ADMIN)

    @admin.display(description='время приготовления')
    def cooking_time_display(self, obj):
        return format_duration_time(obj.cooking_time)

    @admin.display(description='В избранном (раз)')
    def is_favorited(self, obj):
        return obj.fav_count

    @admin.display(description='ингредиенты')
    def get_ingredients(self, obj):
        ingredients = obj.ingredients.all()
        if not ingredients:
            return '—'

        args_list = [
            (
                reverse(
                    'admin:recipes_ingredient_change', args=[ingredient.id]
                ),
                ingredient.name,
            )
            for ingredient in ingredients
        ]
        return render_html_list_block(args_list, 'Показать ингредиенты')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('ingredients').annotate(
            fav_count=Count('favorites')
        )
