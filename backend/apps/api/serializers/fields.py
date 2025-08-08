from rest_framework import serializers

from apps.core.utils import decode_base64_image


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

        if isinstance(data, str) and data.startswith('data:image'):
            try:
                data = decode_base64_image(data)
            except ValueError as e:
                raise serializers.ValidationError(str(e)) from e
        return super().to_internal_value(data)
