from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from apps.api.serializers import Base64ImageField
from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from apps.recipes.services import create_recipe_ingredients
from apps.users.models import Cart, Favorite

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        # fields = '__all__'  # REVIEW: Используй '__all__'


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

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    # id = serializers.IntegerField(source='ingredient.id')  # FIXME:

    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientCreateSerializer(RecipeIngredientBaseSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""


class RecipeIngredientReadSerializer(RecipeIngredientBaseSerializer):
    """Сериализатор для отображения ингредиентов рецепта."""

    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient.measurement_unit', slug_field='name', read_only=True
    )

    class Meta(RecipeIngredientBaseSerializer.Meta):
        fields = (
            *RecipeIngredientBaseSerializer.Meta.fields,
            'name',
            'measurement_unit',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.

    Используется только при записи. Включает валидацию ингредиентов,
    обработку вложенных объектов и логику сохранения.
    """

    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        write_only=True,
        allow_empty=False,
        error_messages={
            'empty': 'Необходимо выбрать хотя бы один ингредиент.',
            'required': 'Поле ингредиентов обязательно для заполнения.',
        },
    )
    image = Base64ImageField(
        required=True,
        allow_null=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False,
        error_messages={
            'empty': 'Необходимо выбрать хотя бы один тег.',
            'required': 'Поле тегов обязательно для заполнения.',  # TODO: Сделать так же в других местах где надо по Redocs
        },
    )  # FIXME: Провалидировать дубли тега или тихо удлаять по умолчанию?

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',  # REVIEW: Добавь поле cooking_time и его валидацию на минимальное значение.
            'author',
        )

    def validate(self, data):
        """
        Валидирует отсутствие полей тегов и ингедиентов.
        Объединяет одинаковые ингредиенты.
        """
        if 'ingredients' in data:
            merged = {}
            for item in data['ingredients']:
                ingredient_id = item['ingredient'].pk
                if ingredient_id in merged:
                    merged[ingredient_id]['amount'] += item['amount']
                else:
                    merged[ingredient_id] = item.copy()
            data['ingredients'] = list(merged.values())

        if 'tags' not in data:
            raise serializers.ValidationError(
                {'tags': 'Поле тегов обязательно для заполнения.'}
            )

        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': 'Поле ингредиентов обязательно для заполнения'}
            )

        return data

    @transaction.atomic
    def create(self, validated_data):
        """Создает рецепт, включая ингредиенты и теги."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = super().create(validated_data)
        create_recipe_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет рецепт, включая ингредиенты и теги."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        instance.recipe_ingredients.all().delete()
        create_recipe_ingredients(instance, ingredients_data)
        instance.tags.set(tags_data)
        return super().update(instance, validated_data)


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецепта.

    Включает вложенные теги, автора, ингредиенты и вычисляемые поля
    избранного и корзины.
    """

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

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли текущим пользователем рецепт в избранное.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если рецепт в избранном, иначе False.
        """
        user = self.context['request'].user
        return (
            user.is_authenticated and obj.favorites.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, находится ли рецепт в корзине текущего пользователя.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если рецепт добавлен в корзину, иначе False.
        """
        user = self.context['request'].user
        return user.is_authenticated and obj.carts.filter(user=user).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения усеченного списка полей рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class CartCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в корзину."""

    class Meta:
        model = Cart
        fields = ('user', 'recipe')
