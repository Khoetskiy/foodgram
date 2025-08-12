from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.api.permissions import DenyAll
from apps.api.serializers import (
    UserAvatarSerializer,
    UserCreateSerializer,
    UserReadSerializer,
)
from apps.api.views import (
    AvatarManagementMixin,
    DisableDjoserActionsMixin,
    SubscriptionMixin,
)
from apps.core.constants import DISABLED_ACTIONS_DJOSER

User = get_user_model()


class CustomUserViewSet(
    DisableDjoserActionsMixin,
    AvatarManagementMixin,
    SubscriptionMixin,
    DjoserUserViewSet,
):
    """
    ViewSet для управления пользователями c расширенной функциональностью.

    Наследуется от UserViewSet Djoser, но отключает ненужные действия
    и добавляет кастомную функциональность:
    - Отключение стандартных Djoser действий (DisableDjoserActionsMixin)
    - Управление аватарами (AvatarManagementMixin)
    - Управление подписками (SubscriptionMixin)
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']  # noqa: RUF012

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'manage_avatar':
            return UserAvatarSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateSerializer
        return UserReadSerializer

    def get_permissions(self):
        """Настройка разрешений для отключенных действий."""
        if self.action in DISABLED_ACTIONS_DJOSER:
            return [DenyAll()]
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод "PUT" не разрешен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод "DELETE" не разрешен.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        """Доступен только для чтения."""
        return super().me(request, *args, **kwargs)
