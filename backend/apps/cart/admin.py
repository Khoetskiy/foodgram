from django.contrib import admin
from django.db.models import Prefetch
from django.urls import reverse

from apps.cart.models import Cart, CartItem
from apps.core.utils import render_recipes_as_html


class CartItemInline(admin.TabularInline):
    """Встраиваемая админка для элементов корзины в админ-панели Cart."""

    model = CartItem
    extra = 0
    fields = ('recipe', 'updated_at', 'created_at')
    readonly_fields = ('updated_at', 'created_at')
    autocomplete_fields = ('recipe',)
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Админ-панель для модели Cart."""

    inlines = (CartItemInline,)
    list_display = ('user', 'get_recipes', 'updated_at', 'created_at')
    search_fields = ('user__username', 'items__recipe__name')
    list_filter = ('updated_at', 'created_at')

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        cartitems = obj.items.all()
        if not cartitems:
            return '—'

        args_list = [
            (
                reverse(
                    'admin:recipes_recipe_change',
                    args=[cartitem.recipe.id],
                ),
                cartitem.recipe,
            )
            for cartitem in cartitems
        ]
        return render_recipes_as_html(args_list)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related(
            Prefetch(
                'items', queryset=CartItem.objects.select_related('recipe')
            )
        )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Админ-панель для модели CartItem."""

    list_display = ('cart', 'recipe', 'updated_at', 'created_at')
    search_fields = ('cart__user__username', 'recipe__name')
    list_filter = ('updated_at', 'created_at')
    autocomplete_fields = ('cart', 'recipe')
