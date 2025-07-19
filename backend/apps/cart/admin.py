from django.contrib import admin

from apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ('recipe', 'updated_at', 'created_at')
    readonly_fields = ('updated_at', 'created_at')
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = (CartItemInline,)
    list_display = ('user', 'updated_at', 'created_at')
    search_fields = ('user',)
    list_filter = ('updated_at', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'recipe', 'created_at', 'updated_at')
    # inlines = (CartItemInline,)
