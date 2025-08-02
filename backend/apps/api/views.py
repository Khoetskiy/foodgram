from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import DenyAll, IsAdminOrReadOnly
from apps.api.serializers import (
    IngredientSerializer,
    # PasswordSetSerializer,
    RecipeSerializer,
    UserAvatarSerializer,
    UserCreateUpdateSerializer,
    UserReadSerializer,
)
from apps.core.constants import DISABLED_ACTIONS_DJOSER
from apps.recipes.models import Ingredient, Recipe

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """
    ViewSet для управления пользователями и получения информации о себе.

    Наследуется от UserViewSet Djoser.

    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserReadSerializer

    def get_permissions(self):
        if self.action in DISABLED_ACTIONS_DJOSER:
            return [DenyAll()]
        return super().get_permissions()


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_avatar(request):
    """Обработка изменения или удаления аватара текущего пользователя."""
    user = request.user

    if request.method == 'PUT':
        serializer = UserAvatarSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if not user.avatar:
            return Response(
                {'detail': 'Аватар уже был удален.'},
                status=status.HTTP_204_NO_CONTENT,
            )
        user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(
            {'detail': 'Аватар успешно удален.'},
            status=status.HTTP_204_NO_CONTENT,
        )

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями и получения информации о себе."""

    queryset = User.objects.all().order_by('date_joined')
    # serializer_class = UserSerializer
    # permission_classes =
    # pagination_class =
    # throttle_classes =
    # http_method_names

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserReadSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,),
    )
    def current_user(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        url_name='me_avatar',
        permission_classes=(IsAuthenticated,),
        # serializer_class=UserAvatarSerializer,
    )
    def manage_avatar(self, request):
        instance = request.user

        if request.method == 'PUT':
            serializer = UserAvatarSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if not instance.avatar:
                return Response(
                    {'detail': 'Аватар уже был удален.'},
                    status=status.HTTP_202_ACCEPTED,
                )
            instance.avatar.delete(save=False)
            instance.avatar = None
            instance.save(update_fields=['avatar'])
            return Response(
                {'detail': 'Аватар успешно удален.'},
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(
    #     detail=False,
    #     methods=['post'],
    #     url_path='set_password',
    #     url_name='set_password',
    #     permission_classes=(IsAuthenticated,),
    # )
    # def set_password(self, request):
    #     serializer = PasswordSetSerializer(
    #         data=request.data, context={'request': request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     user = request.user
    #     user.set_password(serializer.validated_data['new_password'])
    #     user.save()
    #     return Response(
    #         {'detail': 'Пароль успешно изменён'}, status=status.HTTP_200_OK
    #     )
