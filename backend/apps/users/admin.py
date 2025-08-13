from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from apps.core.admin_mixins import (
    BaseSubscribeInlineMixin,
    NoChangeMixin,
    ReadOnlyInLineMixin,
    UserRecipeCollectionAdminMixin,
)
from apps.users.models import Favorite, Favoriteitem, Subscribe

User = get_user_model()

admin.site.unregister(Group)


class SubscriptionsInline(
    BaseSubscribeInlineMixin, NoChangeMixin, admin.TabularInline
):
    """
    Инлайн для отображения подписок пользователя (на кого он подписан).
    """

    fk_name = 'user'

    verbose_name = 'подписка'
    verbose_name_plural = 'подписки (на кого подписан)'


class SubscribersInline(
    BaseSubscribeInlineMixin, NoChangeMixin, admin.TabularInline
):
    """
    Инлайн для отображения подписчиков пользователя (кто на него подписан).
    """

    fk_name = 'author'

    verbose_name = 'подписчик'
    verbose_name_plural = 'подписчики (кто подписан)'


class FavoriteItemInLine(NoChangeMixin, admin.TabularInline):
    """Инлайн для отображения элементов избранного в админ-панели Favorite"""

    model = Favoriteitem
    extra = 0
    fields = ('recipe', 'created_at')
    readonly_fields = ('updated_at', 'created_at')
    autocomplete_fields = ('recipe',)
    verbose_name = 'рецепт'
    verbose_name_plural = 'избранные рецепты'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('favorite', 'recipe', 'favorite__user')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Админ-класс для модели пользователя.

    Включает:
        - Инлайн-класс SubscriptionsInline для подписок пользователя.
        - Инлайн-класс SubscribersInline для подписчиков пользователя.
    """

    inlines = (SubscriptionsInline, SubscribersInline)
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


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeCollectionAdminMixin, admin.ModelAdmin):
    """
    Админ-панель для модели Favorite.
    Отображает список избранных рецептов пользователей.

    Включает:
        - Инлайн-класс FavoriteItemInLine для управления избранными рецептами.
    """

    inlines = (FavoriteItemInLine,)
    model_item = Favoriteitem


@admin.register(Subscribe)
class SubscribeAdmin(ReadOnlyInLineMixin, admin.ModelAdmin):
    """Админ-панель для модели Subscribe."""

    list_display = ('user', 'author')
    readonly_fields = ('user', 'author')
    search_fields = ('user__username', 'author__username')
    list_filter = ('updated_at', 'created_at')
