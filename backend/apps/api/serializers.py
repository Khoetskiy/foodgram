import base64

import django.contrib.auth.password_validation as validators

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from apps.core.utils import decode_base64_image, generate_unique_filename
from apps.recipes.models import Ingredient, MeasurementUnit, Recipe, Tag
from apps.users.models import Subscribe

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




