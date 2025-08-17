from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.api.serializers import Base64ImageField, RecipeShortSerializer
from apps.users.models import Subscribe

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных пользователя (GET-запросы).

    Включает вычисляемое поле `is_subscribed`, показывающее,
    подписан ли текущий пользователь на отображаемого автора.

    Attributes:
        is_subscribed (SerializerMethodField): Вычисляемое поле.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

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
            bool: True, user подписан на obj, иначе False.
        """
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.subscribers.filter(user=user).exists()
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя (POST-запросы).

    Используется при регистрации. Поле `password` доступно только для записи.
    """

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
        extra_kwargs = {'password': {'write_only': True}}  # noqa: RUF012

    def create(self, validate_data):
        """Создаёт пользователя и хэширует пароль."""
        return User.objects.create_user(**validate_data)


class UserAvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления аватара пользователя.

    Attributes:
        avatar (Base64ImageField): Кастомное поле для загрузки изображения.
    """

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionUserSerializer(UserReadSerializer):
    """
    Сериализатор для отображения подписок пользователя.

    Расширяет базовый UserReadSerializer, добавляя:
    - Список рецептов автора (поле `recipes`)
    - Количество рецептов автора (поле `recipes_count`)

    Attributes:
        recipes_count (SerializerMethodField): Количество рецептов автора.
        recipes (SerializerMethodField): Список рецептов в сокращённой форме.
    """

    recipes_count = serializers.IntegerField(read_only=True)
    recipes = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = (*UserReadSerializer.Meta.fields, 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """
        Вычисляемое поле, возвращающее список рецептов автора.

        Ограниченный параметром recipes_limit.

        Args:
            obj (User): Автор, чьи рецепты нужно получить.

        Returns:
            list: Список рецептов ограниченный по количеству.
        """
        limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit is not None:
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        """Дополнительная валидация - нельзя подписаться на себя."""
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                {'detail': 'Нельзя подписаться на самого себя'}
            )
        return super().validate(data)
