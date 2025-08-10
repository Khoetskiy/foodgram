from django.contrib import admin
from django.db.models import Prefetch

from apps.core.services import get_objects
from apps.users.models import Subscribe


class NoAddMixin:
    """Mixin для запрета добавления объектов через админку."""

    show_change_link = True

    def has_add_permission(self, requst, obj=None):
        """Запрет добавления новых объектов."""
        return False


class NoChangeMixin:
    """Mixin для запрета изменения объектов через админку."""

    show_change_link = True

    def has_change_permission(self, request, obj=None):
        """Запрет редактирования существующих объектов."""
        return False


class NoDeleteMixin:
    """Mixin для запрета удаления объектов через админку."""

    show_change_link = True
    can_delete = False

    def has_delete_permission(self, request, obj=None):
        """Запрет удаления объектов через админку."""
        return False


class ReadOnlyInLineMixin(NoAddMixin, NoChangeMixin, NoDeleteMixin):
    """
    Mixin для админских инлайнов, который запрещает
    добавление, изменение и удаление объектов.
    """


class BaseSubscribeInlineMixin:
    """Базовый миксин для инлайнов подписок."""

    model = Subscribe
    extra = 0
    readonly_fields = ('created_at',)

    def get_field(self, request, obj=None):
        """Поля определяются в зависимости от fk_name."""
        if self.fk_name == 'user':
            return ('author', 'created_at')
        if self.fk_name == 'author':
            return ('user', 'created_at')
        return super().get_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'author')


class UserRecipeCollectionAdminMixin:
    """
    Миксин для админ-панелей коллекций пользователей (избранное, корзина).
    """

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

    model_item = None

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
        qs = qs.select_related('user')

        if self.model_item:
            qs = qs.prefetch_related(
                Prefetch(
                    'items',
                    queryset=self.model_item.objects.select_related('recipe'),
                )
            )
        return qs  # [ ]: Получше разобраться как это работает Prefetch
