import base64

import django.contrib.auth.password_validation as validators

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from apps.cart.models import CartItem
from apps.core.utils import decode_base64_image, generate_unique_filename
from apps.recipes.models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeIngredient,
    Tag,
)
from apps.users.models import Favoriteitem, Subscribe

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()  # FIXME: read_only?

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """
        Вычисляемое поле, показывающее статус подписки пользователя на автора.

        Args:
            obj (User): Автор, на которого может быть подписка.

        Returns:
            bool: True, если request.user подписан на obj, иначе False.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}  # noqa: RUF012

        def create(self, validate_data):
            return User.objects.create_user(**validate_data)

        # def create(self, validate_data):
        #     password = validate_data.pop('password')
        #     user = User(**validate_data)
        #     user.set_password(password)
        #     user.save()
        #     return user


class Base64ImageField(serializers.ImageField):
    """
    Кастомное поле сериализатора для загрузки изображений в формате base64.

    Ожидает строку формата data:image/<ext>;base64,<код> и
    преобразует её в объект Django ContentFile для сохранения.
    """

    def to_internal_value(self, data):
        """
        Преобразует входные данные в объект изображения.

        Если строка base64, то происходит декодирование и преобразование
                                        в ContentFile c уникальным именем.
        Иначе данные передаются стандартному обработчику родительского класса.

        Args:
            data (str|File): Входные данные (base64-строка или файл).

        Returns:
            File: Объект файла изображения для сохранения.

        Raises:
            serializers.ValidationError: При ошибке декодирования base64-строки
        """
        # if not data:
        #     if self.required:
        #         self.fail('required')
        #     return None

        if isinstance(data, str) and data.startswith('data:image'):
            try:
                data = decode_base64_image(data)
            except ValueError as e:
                raise serializers.ValidationError(str(e)) from e
        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления аватара пользователя.

    Attributes:
        avatar (Base64ImageField): Кастомное поле для загрузки изображения.
    """

    avatar = Base64ImageField(required=True, allow_null=False)
    # BUG: не то смс об пустом поле выводиться
    # avatar = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        if not value:
            raise serializers.ValidationError('Обязательное поле.')
        return value

    def validate(self, attrs):
        if 'avatar' not in attrs or not attrs.get('avatar'):
            raise serializers.ValidationError(
                {'avatar': 'Это поле обязательно.'}
            )
        return attrs

    # FIXME: Убрать валидацию?


# NOTE: Заменил на встроенную в Djoser
class PasswordSetSerializer(serializers.Serializer):
    """"""

    current_password = serializers.CharField(
        required=True, label='Текущий пароль'
    )
    new_password = serializers.CharField(required=True, label='Новый пароль')

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Неверный текущий пароль')
        return value

    def validate_new_password(self, value):
        validators.validate_password(value)
        return value


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    # measurement_unit = serializers.StringRelatedField(many=False)
    measurement_unit = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name'
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class BaseRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientCreateSerializer(BaseRecipeIngredientSerializer):
    pass


class RecipeIngredientReadSerializer(BaseRecipeIngredientSerializer):
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.name', read_only=True
    )

    class Meta(BaseRecipeIngredientSerializer.Meta):
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


# class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='ingredient.id')
#     amount = serializers.IntegerField(min_value=1)

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount')


# class RecipeIngredientReadSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='ingredient.id', read_only=True)
#     name = serializers.CharField(source='ingredient.name', read_only=True)
#     measurement_unit = serializers.CharField(
#         source='ingredient.measurement_unit.name', read_only=True
#     )

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'measurement_unit', 'amount')


# TODO: вынести в общие миксины повторяющейся код и наследоваться от него, особенно где два сериализатора чтение/запись


# XXX: Как вернуть сигнал и логику создания пути файла?
class RecipeWriteSerializer(serializers.ModelSerializer):
    """"""

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

    def _create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient_data['ingredient']['id'],
                    amount=ingredient_data['amount'],
                )
                for ingredient_data in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        if ingredients_data:
            self._create_ingredients(recipe, ingredients_data)

        if tags_data:
            recipe.tags.set(tags_data)

        return recipe

    # def to_representation(self, instance):
    #     # FIXME: Решить где это реализовывать?
    #     return RecipeReadSerializer(instance, context=self.context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserReadSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
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

    def _get_authenticated_user(self):
        """
        Возвращает пользователя, если он авторизован, иначе None.

        Returns:
            User | None: Объект пользователя, либо None.
        """
        user = self.context['request'].user
        return user if user.is_authenticated else None

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли текущим пользователем рецепт в избранное.

        Args:
            obj: Объект рецепта.

        Returns:
            bool: True, если рецепт в избранном у пользователя, иначе False.
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


# =============================================================================


# class IngredientModel:
#     def __init__(self, name, measurement_unit_id) -> None:
#         self.name = name
#         self.measurement_unit_id = measurement_unit_id


class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    measurement_unit_id = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Ingredient.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.measurement_unit_id = validated_data.get(
            'measurement_unit_id', instance.measurement_unit_id
        )
        instance.updated_at = validated_data.get(
            'updated_at', instance.updated_at
        )
        instance.save()
        return instance


# def encode():
#     model = IngredientModel('apple', 7)
#     model_sr = IngredientSerializer(model)
#     print(model_sr.data, type(model_sr.data), sep='\n')
#     json = JSONRenderer().render(model_sr.data)
#     print(json)


# def decode():
#     stream = io.BytesIO(b'{"name":"apple","measurement_unit_id":7}')
#     data = JSONParser().parse(stream)
#     serializers = IngredientSerializer(data=data)
#     serializers.is_valid()
#     print(serializers.validated_data)
