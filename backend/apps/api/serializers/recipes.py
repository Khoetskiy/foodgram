from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from apps.api.serializers import Base64ImageField
from apps.cart.models import CartItem
from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from apps.recipes.services import create_recipe_ingredients
from apps.users.models import Favoriteitem

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    measurement_unit = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name'
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientBaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для ингредиентов в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientCreateSerializer(RecipeIngredientBaseSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""


class RecipeIngredientReadSerializer(RecipeIngredientBaseSerializer):
    """Сериализатор для отображения ингредиентов рецепта."""

    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.name', read_only=True
    )

    class Meta(RecipeIngredientBaseSerializer.Meta):
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.

    Используется только при записи. Включает валидацию ингредиентов,
    обработку вложенных объектов и логику сохранения.
    """

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientCreateSerializer(many=True, write_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )

    def validate_ingredients(self, value):
        """
        Проверяет список ингредиентов на пустоту, дубликаты и существование.
        """
        if not value:
            msg = 'Список ингредиентов не может быть пустым'
            raise serializers.ValidationError(msg)

        ingredient_ids = [item['ingredient']['id'] for item in value]
        existing_ingredients = Ingredient.objects.filter(pk__in=ingredient_ids)

        if len(ingredient_ids) != len(set(ingredient_ids)):
            msg = 'Ингредиенты не должны повторяться'
            raise serializers.ValidationError(msg)

        if len(existing_ingredients) != len(ingredient_ids):
            msg = 'Один или несколько ингредиентов не существуют'
            raise serializers.ValidationError(msg)

        return value

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт, включая ингредиенты и теги."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        if ingredients_data:
            create_recipe_ingredients(recipe, ingredients_data)

        if tags_data:
            recipe.tags.set(tags_data)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт, включая ингредиенты и теги."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            create_recipe_ingredients(instance, ingredients_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        return instance


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецепта.

    Включает вложенные теги, автора, ингредиенты и вычисляемые поля
    избранного и корзины.
    """
    # FIXME: подумать
    # author = UserReadSerializer(many=False, read_only=True)
    author = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_author(self, obj):
        """Lazy import для UserReadSerializer"""
        from .users import UserReadSerializer

        return UserReadSerializer(obj.author, context=self.context).data

    def _get_authenticated_user(self):
        """
        Возвращает пользователя, если он авторизован.

        Returns:
            User | None: Авторизованный пользователь или None.
        """
        user = self.context['request'].user
        return user if user.is_authenticated else None

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли текущим пользователем рецепт в избранное.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если рецепт в избранном, иначе False.
        """
        user = self._get_authenticated_user()
        return Favoriteitem.objects.filter(
            recipe=obj, favorite__user=user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, находится ли рецепт в корзине текущего пользователя.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если рецепт добавлен в корзину, иначе False.
        """
        user = self._get_authenticated_user()
        return CartItem.objects.filter(recipe=obj, cart__user=user).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения усеченного списка полей рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
