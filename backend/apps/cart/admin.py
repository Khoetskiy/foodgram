# TODO: Сделать регистронезависымый поиск на кириллице

from django.contrib import admin

from apps.cart.models import Cart, CartItem
from apps.core.admin_mixins import UserRecipeCollectionAdminMixin


class CartItemInline(admin.TabularInline):
    """Inline-форма для отображения элементов корзины в админке модели Cart."""

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
class CartAdmin(UserRecipeCollectionAdminMixin, admin.ModelAdmin):
    """Админ-панель для корзины пользователя."""

    inlines = (CartItemInline,)
    model_item = CartItem
