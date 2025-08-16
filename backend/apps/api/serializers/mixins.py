from rest_framework import serializers


class BaseRelationCreateSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для создания связей пользователя c объектами."""


    class Meta:
        abstract = True
# TODO: Delete?
