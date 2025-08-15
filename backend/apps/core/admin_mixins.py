from django.contrib import admin

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
    """Базовый класс для Inline подписок."""

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


class UserRecipeCollectionAdminMixin(admin.ModelAdmin):
    """
    Миксин для админ-панелей коллекций пользователей избранного и корзины.
    """

    list_display = ('user', 'recipe', 'created_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'created_at')
    date_hierarchy = 'created_at'


class BaseRecipeCollectionInLineMixin(admin.TabularInline):
    """
    Базовый класс для Inline коллекций пользователей избранного и корзины.
    """

    model = None
    extra = 0
    classes = ('collapse',)
    fields = ('recipe', 'created_at')
    readonly_fields = ('created_at',)
    verbose_name = 'рецепт'
    verbose_name_plural = ''

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'recipe')
