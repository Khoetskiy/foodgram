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
