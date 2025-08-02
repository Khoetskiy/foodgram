# TODO: Настроить регистронезависимый поиск по названию (вхождение в начало, опционально — в произвольном месте)  # noqa: E501

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Prefetch

from apps.core.admin_mixins import NoChangeMixin, ReadOnlyInLineMixin
from apps.core.services import get_objects
from apps.users.models import Favorite, Favoriteitem, Subscribe

User = get_user_model()

admin.site.unregister(Group)


class SubscriptionsInline(NoChangeMixin, admin.TabularInline):
    """
    Инлайн для отображения подписок пользователя (на кого он подписан).
    """

    model = Subscribe
    extra = 0
    fk_name = 'user'
    fields = ('author', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = 'подписка'
    verbose_name_plural = 'подписки (на кого подписан)'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'author')


class SubscribersInline(NoChangeMixin, admin.TabularInline):
    """
    Инлайн для отображения подписчиков пользователя (кто на него подписан).
    """

    model = Subscribe
    extra = 0
    fk_name = 'author'
    fields = ('user', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = 'подписчик'
    verbose_name_plural = 'подписчики (кто подписан)'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'author')


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
class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Favorite.
    Отображает список избранных рецептов пользователей.

    Включает:
        - Инлайн-класс FavoriteItemInLine для управления избранными рецептами.
    """

    inlines = (FavoriteItemInLine,)
    list_display = ('user', 'get_recipes', 'updated_at', 'created_at')
    list_filter = ('updated_at', 'created_at')
    search_fields = ('user__username', 'items__recipe__name')
    readonly_fields = ('updated_at', 'created_at')
    fieldsets = (
        (None, {'fields': ('user',)}),
        (
            'Системная информация',
            {
                'fields': ('updated_at', 'created_at'),
                'classes': ('extrapretty',),
            },
        ),
    )

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        """Возвращает связанные рецепты, в виде списка HTML-блока."""
        return get_objects(
            items=obj.items.all(),
            admin_url='admin:recipes_recipe_change',
            item_args=lambda item: [item.recipe.id],
            display_value=lambda item: item.recipe,
            title='Показать рецепты',
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            Prefetch(
                'items', queryset=Favoriteitem.objects.select_related('recipe')
            ),
        )  # XXX: Уточнить как работает и для корзины?


# # TODO: Удалить из-за ненадобности?
@admin.register(Subscribe)
class SubscribeAdmin(ReadOnlyInLineMixin, admin.ModelAdmin):
    """Админ-панель для модели Subscribe."""

    list_display = ('user', 'author')
    readonly_fields = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('updated_at', 'created_at')


# TODO: Удалить из-за ненадобности?
# @admin.register(Favoriteitem)
# class FavoriteItemAdmin(admin.ModelAdmin):
#     """Админ-панель для модели FavoriteItem."""

#     list_display = ('favorite', 'recipe', 'updated_at', 'created_at')
#     search_fields = ('favorite__user__username', 'recipe__name')
#     list_filter = ('updated_at', 'created_at')
#     autocomplete_fields = ('favorite', 'recipe')
