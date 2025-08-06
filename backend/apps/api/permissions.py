from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает только безопасные методы всем пользователям.
    Изменяющие методы доступны только администратору.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user and request.user.is_staff
        )


class DenyAll(BasePermission):
    """Полный запрет доступа для всех пользователей и всех методов."""

    def has_permission(self, request, view):
        return False


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешает безопасные методы всем пользователям.
    Изменяющие методы доступны только автору объекта.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user

# FIXME: Есть ли неиспользуемые permissions? Ели да, то удалить
