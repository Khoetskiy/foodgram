class ReadOnlyInLineMixin:
    """
    Mixin для админских инлайнов, который запрещает
    добавление, изменение и удаление объектов.
    """

    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """Запрет добавления новых объектов."""
        return False

    def has_change_permission(self, request, obj=None):
        """Запрет редактирования существующих объектов."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Запрет удаления объектов через админку."""
        return False
