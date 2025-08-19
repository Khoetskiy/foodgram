from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.pagination import LimitPageNumberPagination
from apps.api.serializers import (
    CartCreateSerializer,
    FavoriteCreateSerializer,
    RecipeShortSerializer,
    SubscriptionUserSerializer,
    UserAvatarSerializer,
)
from apps.api.serializers.users import SubscribeCreateSerializer
from apps.core.constants import SHORT_LINK_PREFIX
from apps.recipes.models import RecipeIngredient
from apps.recipes.services import (
    get_txt_in_response,
    manage_user_relation_object,
)
from apps.users.models import Cart, Favorite, Subscribe

User = get_user_model()


class DisableDjoserActionsMixin:
    """
    Миксин для отключения ненужных действий Djoser.

    Переопределяет стандартные методы Djoser и возвращает 404,
    эффективно скрывая эти эндпоинты от пользователей.
    """

    def activation(self, request, *args, **kwargs):
        raise NotFound

    def resend_activation(self, request, *args, **kwargs):
        raise NotFound

    def reset_password(self, request, *args, **kwargs):
        raise NotFound

    def reset_password_confirm(self, request, *args, **kwargs):
        raise NotFound

    def set_username(self, request, *args, **kwargs):
        raise NotFound

    def reset_username(self, request, *args, **kwargs):
        raise NotFound

    def reset_username_confirm(self, request, *args, **kwargs):
        raise NotFound


class AvatarManagementMixin:
    """
    Миксин для управления аватаром пользователя.

    Предоставляет возможность загрузки и удаления аватара
    через отдельный эндпоинт `me/avatar`.
    """

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        url_name='me_avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        """Загрузка нового аватара."""
        serializer = UserAvatarSerializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара пользователя."""
        user = request.user
        if not user.avatar:
            return Response(
                {'detail': 'Аватар отсутствует.'},
                status=status.HTTP_204_NO_CONTENT,
            )
        user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(
            {'detail': 'Аватар успешно удален.'},
            status=status.HTTP_204_NO_CONTENT,
        )


class SubscriptionMixin:
    """
    Миксин для управления подписками пользователей.

    Предоставляет возможность просмотра подписок и
    подписки/отписки от авторов.
    """

    @action(
        detail=False,
        methods=['get'],
        url_name='subscriptions',
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Возвращает подписки текущего пользователя."""
        subscriptions = Subscribe.objects.filter(user=request.user)
        authors = self.get_queryset().filter(
            pk__in=subscriptions.values('author')
        )
        paginator = LimitPageNumberPagination()
        paginated_authors = paginator.paginate_queryset(authors, request)
        serializer = SubscriptionUserSerializer(
            paginated_authors,
            many=True,
            context={'request': request},
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='subscribe',
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def manage_subscribe(self, request, **kwargs):
        """Подписка или отписка от пользователя."""
        author = self.get_object()

        handler = manage_user_relation_object(
            relation_model=Subscribe,
            user_id=request.user.id,
            target_field='author',
            target_object_id=author.id,
            target_object=author,
            create_serializer=SubscribeCreateSerializer,
            response_serializer=SubscriptionUserSerializer,
            context={'request': request},
            not_found_error='Вы не были подписаны на этого автора',
        )
        return handler(request)

    def get_queryset(self):
        """Добавляет аннотацию для `recipes_count`."""
        return super().get_queryset().annotate(recipes_count=Count('recipes'))


class FavoriteManagerMixin:
    """
    Миксин для управления избранными рецептами пользователя.

    Предоставляет возможность добавления и удаления рецептов из избранного.
    """

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='favorite',
        url_path='favorite',
        permission_classes=[IsAuthenticated],
    )
    def manage_favorite(self, request, **kwargs):
        """Добавление или удаление рецепта из избранного."""
        recipe = self.get_object()

        handler = manage_user_relation_object(
            relation_model=Favorite,
            user_id=request.user.id,
            target_field='recipe',
            target_object_id=recipe.id,
            target_object=recipe,
            create_serializer=FavoriteCreateSerializer,
            response_serializer=RecipeShortSerializer,
            context={'request': request},
            not_found_error='Вы не добавляли этот рецепт в избранное',
        )
        return handler(request)


class ShoppingCartManagerMixin:
    """
    Миксин для управления корзиной покупок пользователя.

    Предоставляет функциональность:
    - Добавления/удаления рецептов в/из корзины
    - Скачивания списка ингредиентов в формате TXT
    """

    @action(
        detail=False,
        methods=['get'],
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """
        Генерирует и возвращает txt-файл со списком покупок пользователя.

        Объединяет все ингредиенты из рецептов,
        суммируя количества одинаковых ингредиентов.
        """
        ingredients = self._get_shopping_ingredients(request.user)
        if not ingredients.exists():
            return Response(
                {'detail': 'Корзина пуста'}, status=status.HTTP_404_NOT_FOUND
            )
        return get_txt_in_response(ingredients)

    def _get_shopping_ingredients(self, user):
        """Возвращает queryset ингредиентов."""
        return (
            RecipeIngredient.objects.filter(recipe__in_carts__cart__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit__name',
            )
            .annotate(
                amount=Sum('amount'),
            )
            .order_by(
                'ingredient__name',
            )
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_name='shopping_cart',
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def manage_shopping_cart(self, request, **kwargs):
        """Добавление или удаление рецепта из корзины."""
        recipe = self.get_object()

        handler = manage_user_relation_object(
            relation_model=Cart,
            user_id=request.user.id,
            target_field='recipe',
            target_object_id=recipe.id,
            target_object=recipe,
            create_serializer=CartCreateSerializer,
            response_serializer=RecipeShortSerializer,
            context={'request': request},
            not_found_error='Вы не добавляли этот рецепт в корзину',
        )
        return handler(request)


class ShortLinkMixin:
    """
    Миксин для работы c короткими ссылками на рецепты.

    Предоставляет функциональность генерации коротких ссылок
    для удобного шаринга рецептов.
    """

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        url_name='get-link',
    )
    def get_short_link(self, request, **kwargs):
        """Возвращает короткую ссылку на рецепт по его short_code."""
        recipe = self.get_object()

        if not hasattr(recipe, 'short_code') or not recipe.short_code:
            return Response(
                {'detail': 'Короткая ссылка для рецепта недоступна'},
                status=status.HTTP_404_NOT_FOUND,
            )

        domain = request.build_absolute_uri('/')[:-1]
        short_url = f'{domain}/{SHORT_LINK_PREFIX}/{recipe.short_code}/'
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)
