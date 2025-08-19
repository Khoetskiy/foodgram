import re

from django.utils.text import slugify

from apps.core.exceptions import SlugGenerationError, TranslationError
from apps.core.utils.text import is_cyrillic, translate_text


def create_slug(text: str, allow_unicode: bool = False) -> str:
    """
    Создаёт slug из текста. Если в тексте кириллица — переводит на английский.

    Args:
        text: Исходный текст для создания slug.
        allow_unicode: Разрешить символы Unicode в slug.

    Raises:
        ValueError: Если текст пустой.
        SlugGenerationError: Если не удалось создать slug.

    Returns:
        str: Сгенерированный slug.
    """
    if not text:
        msg = '"text" не может быть пустым'
        raise ValueError(msg)

    if is_cyrillic(text):
        try:
            text = translate_text(text, 'en')
            slug = slugify(text, allow_unicode=allow_unicode)
        except TranslationError:
            slug = slugify(text, allow_unicode=True)
    else:
        slug = slugify(text, allow_unicode=allow_unicode)

    if not slug:
        msg = 'Не удалось сгенерировать slug из переданного значения.'
        raise SlugGenerationError(msg)

    return slug


def parse_slug_number(slug: str) -> tuple[str, int | None]:
    """
    Разделяет slug и числовой суффикс, если есть.

    Args:
        slug (str): Исходный slug, возможно c числовым суффиксом.

    Returns:
        tuple[str, int | None]: slug и стартовое число для итерации.
    """
    match = re.match(r'^(.*?)-(\d+)$', slug)
    if match:
        slug, number = match.groups()
        return slug, int(number) + 1
    return slug, None


def append_number_to_slug(slug: str, number: int) -> str:
    """
    Добавляет числовой суффикс к slug.

    Args:
        slug (str): Базовый slug.
        number (int): Число для добавления.

    Returns:
        str: Новый slug c числовым суффиксом.
    """
    return f'{slug}-{number}'
