from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from apps.core.admin_mixins import (
    BaseRecipeCollectionInLineMixin,
    BaseSubscribeInlineMixin,
    NoChangeMixin,
    UserRecipeCollectionAdminMixin,
)
from apps.users.models import Cart, Favorite, Subscribe

User = get_user_model()

admin.site.unregister(Group)


class SubscriptionsInline(
    BaseSubscribeInlineMixin, NoChangeMixin, admin.TabularInline
):
    """
    Inline для отображения подписок пользователя (на кого он подписан).
    """

    fk_name = 'user'

    verbose_name = 'подписка'
    verbose_name_plural = 'подписки (на кого подписан)'


class SubscribersInline(
    BaseSubscribeInlineMixin, NoChangeMixin, admin.TabularInline
):
    """
    Inline для отображения подписчиков пользователя (кто на него подписан).
    """

    fk_name = 'author'

    verbose_name = 'подписчик'
    verbose_name_plural = 'подписчики (кто подписан)'


class CartInline(NoChangeMixin, BaseRecipeCollectionInLineMixin):
    """
    Inline для управления корзиной пользователя.

    Позволяет добавлять/удалять рецепты прямо из админки пользователя.
    """

    model = Cart
    verbose_name_plural = 'корзина покупок'


class FavoriteInline(NoChangeMixin, BaseRecipeCollectionInLineMixin):
    """
    Inline для управления избранным пользователя.

    Позволяет добавлять/удалять рецепты прямо из админки пользователя.
    """

    model = Favorite
    verbose_name_plural = 'избранное'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админ-класс для модели пользователя.

    Включает:
        - Инлайн-класс SubscriptionsInline для подписок пользователя.
        - Инлайн-класс SubscribersInline для подписчиков пользователя.
    """

    inlines = (
        SubscriptionsInline,
        SubscribersInline,
        CartInline,
        FavoriteInline,
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'avatar')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = '-'
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Персональная информация',
            {'fields': ('username', 'first_name', 'last_name')},
        ),
        ('Фото', {'fields': ('avatar',)}),
        (
            'Разрешения',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'user_permissions',
                ),
                'classes': ('collapse',),
            },
        ),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('last_login', 'date_joined')
    add_fieldsets = (
        (
            None,
            {
                'classes': ('extrapretty',),
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'username',
                    'first_name',
                    'last_name',
                ),
            },
        ),
    )


@admin.register(Subscribe)
class SubscribeAdmin(NoChangeMixin, admin.ModelAdmin):
    """Админ-панель для модели Subscribe."""

    list_display = ('user', 'author', 'created_at')
    search_fields = ('user__username', 'author__username')
    list_filter = ('user', 'author')
    date_hierarchy = 'created_at'


@admin.register(Cart)
class CartAdmin(NoChangeMixin, UserRecipeCollectionAdminMixin):
    """Админ-панель для корзины пользователя."""


@admin.register(Favorite)
class FavoriteAdmin(NoChangeMixin, UserRecipeCollectionAdminMixin):
    """Админ-панель для избранного пользователя."""
