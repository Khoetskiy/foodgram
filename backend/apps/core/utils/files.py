import logging

from pathlib import Path
from uuid import uuid4

import base64
from uuid import uuid4
from django.core.files.base import ContentFile

from apps.core.constants import (
    ALLOWED_EXTENSIONS,
    DEFAULT_EXT,
    UUID_FILENAME_LENGTH,
)

logger = logging.getLogger(__name__)


def get_safe_extension(filename: str) -> str:
    # REVIEW: Убрать, тк валидация в поле image модели Recipe?
    """
    Получает безопасное расширение файла, если оно разрешено.

    Проверяет наличие и допустимость расширения файла.
    Если расширение отсутствует или не входит в список допустимых,
    возвращает значение по умолчанию.

    Args:
        filename (str): Имя файла, включая расширение.

    Returns:
        str: Безопасное расширение.
    """
    ext = Path(filename).suffix
    if not ext or ext.lower().lstrip('.') not in ALLOWED_EXTENSIONS:
        msg = f'Файл: "{filename}" без расширения или недопустимое расширение'
        logger.warning(msg)
        return f'.{DEFAULT_EXT}'
    return ext.lower()


def generate_unique_filename(ext: str) -> str:
    """
    Генерирует уникальное имя файла.

    Args:
        ext (str): расширение файла.

    Returns:
        str: уникальное название файла.
    """
    return f'{uuid4().hex[:UUID_FILENAME_LENGTH]}{ext}'


def decode_base64_image(data: str):
    """
    Декодирует строку формата data:image/png;base64,<...> в ContentFile.

    Args:
        data (str): Строка c изображением в формате data:image/...;base64,...

    Returns:
        ContentFile: Объект для сохранения изображения.

    Raises:
        ValueError: Если строка не может быть декодирована.
    """
    try:
        mimetype, imgstr = data.split(';base64,')
        ext = mimetype.split('/')[-1]
        filename = generate_unique_filename(f'.{ext}')
        return ContentFile(base64.b64decode(imgstr), filename)
    except Exception as e:
        msg = 'Некорректные данные изображения.'
        raise ValueError(msg) from e
