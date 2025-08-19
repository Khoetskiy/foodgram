# ruff: noqa: RUF012
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api.filters import IngredientFilter, RecipeFilter
from apps.api.pagination import LimitPageNumberPagination
from apps.api.permissions import IsAuthorOrReadOnly
from apps.api.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from apps.api.views import (
    FavoriteManagerMixin,
    ShoppingCartManagerMixin,
    ShortLinkMixin,
)
from apps.recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для получения информации o тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Ingredient.

    Поддерживает поиск по частичному вхождению в начале названия ингредиента.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(
    FavoriteManagerMixin,
    ShoppingCartManagerMixin,
    ShortLinkMixin,
    viewsets.ModelViewSet,
):
    """
    ViewSet для управления рецептами c расширенной функциональностью.

    Основная функциональность:
    - CRUD операции c рецептами
    - Фильтрация по избранному, автору, корзине покупок и тегам
    - Пагинация c настройкой лимита
    - Управление избранными рецептами
    - Управление корзиной покупок
    - Генерация коротких ссылок
    """

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient__measurement_unit'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer
