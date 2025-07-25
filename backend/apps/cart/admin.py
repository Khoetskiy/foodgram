# TODO: Сделать регистронезависымый поиск на кириллице

from django.contrib import admin
from django.db.models import Prefetch

from apps.cart.models import Cart, CartItem
from apps.core.services import get_objects


class CartItemInline(admin.TabularInline):
    """Инлайн для отображения элементов корзины в админке модели Cart."""

    model = CartItem
    extra = 0
    fields = ('recipe', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('recipe',)
    show_change_link = True
    verbose_name = 'рецепт'
    verbose_name_plural = 'элементы корзины'

    def has_change_permission(self, request, obj=None):
        """Запрещает редактирование CartItem из Inline в админке Cart."""
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('cart__user', 'recipe')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админ-панель для корзины пользователя."""

    inlines = (CartItemInline,)
    list_display = ('user', 'get_recipes', 'updated_at', 'created_at')
    search_fields = ('user__username', 'items__recipe__name')
    list_filter = ('updated_at', 'created_at')

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        """Отображает связанные рецепты, как HTML-блок со списком объектов."""
        return get_objects(
            items=obj.items.all(),
            admin_url='admin:recipes_recipe_change',
            item_args=lambda item: [item.recipe.id],
            display_value=lambda item: item.recipe,
            title='Показать рецепты',
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related(
            Prefetch(
                'items', queryset=CartItem.objects.select_related('recipe')
            )
        )  # REVIEW: Получше разобраться как это работает


# FIXME: Убрать из-за ненадобности
# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     """Админ-панель для модели CartItem."""

#     list_display = ('cart', 'recipe', 'updated_at', 'created_at')
#     search_fields = ('cart__user__username', 'recipe__name')
#     list_filter = ('updated_at', 'created_at')
#     autocomplete_fields = ('cart', 'recipe')
