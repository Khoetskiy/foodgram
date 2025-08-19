import re
import uuid

from deep_translator import GoogleTranslator

from apps.core.constants import (
    RECIPE_SHORT_CODE_MAX_LENGTH,
    TEXT_TRUNCATE_LENGTH,
    TEXT_TRUNCATE_SUFFIX,
)
from apps.core.exceptions import TranslationError


def truncate_text(
    text: str,
    length: int = TEXT_TRUNCATE_LENGTH,
    suffix: str = TEXT_TRUNCATE_SUFFIX,
) -> str:
    """
    Обрезает текст и добавляет суффикс, если он превышает указанную длину.

    Args:
        text (str): Исходный текст для обрезки.
        length (int):
            Максимальная длина результирующей строки.
            По умолчанию используется значение `TEXT_TRUNCATE_LENGTH`.
        suffix:
            Суффикс, добавляемый к обрезанному тексту.
            По умолчанию используется значение `TEXT_TRUNCATE_SUFFIX`.

    Returns:
        str: Обрезанный текст или исходный, если он короче указанной длины.

    Raises:
        ValueError: Если length меньше длины suffix.
    """
    if length < len(suffix):
        msg = 'Длина текста не может быть меньше длины суффикса'
        raise ValueError(msg)

    if len(text) > length:
        return f'{text[: length - len(suffix)]}{suffix}'
    return text


def translate_text(text: str, target_language: str = 'en') -> str:
    """
    Переводит текст на указанный язык c помощью GoogleTranslator.
    По умолчанию — на английский.

    Args:
        text (str): Исходный текст.
        target_language (str): Язык перевода.

    Raises:
        TranslationError: Если не удалось выполнить перевод.

    Returns:
        str: Переведённый текст.
    """
    try:
        return GoogleTranslator(
            source='auto', target=target_language
        ).translate(text)
    except Exception as e:
        msg = 'Не удалось перевести текст.'
        raise TranslationError(msg) from e


def is_cyrillic(text: str) -> bool:
    """
    Проверяет текст на кириллицу.

    Args:
        text (str): Исходный текст.

    Returns:
        bool: True, если в тексте есть кириллица.
    """
    return bool(re.search(r'[а-яА-Я]', text))


def capitalize_name(name: str | None) -> str:
    """
    Нормализует имя или фамилию: первая буква — заглавная, далее строчные.

    Удаляет пробелы по краям, приводит строку к виду: "Иван", "Мария", и т.п.
    Если входное значение не строка — возвращает пустую строку.

    Args:
        name (str | None): Имя или фамилия для нормализации. Может быть None.

    Returns:
        str: Нормализованная строка или пустая строка, если вход невалиден.
    """
    if not isinstance(name, str):
        return ''
    return name.strip().capitalize()


def generate_short_code(length: int = RECIPE_SHORT_CODE_MAX_LENGTH) -> str:
    """
    Генерирует короткий код на основе UUID4.

    Args:
        length (int): Максимальная длина.

    Returns:
        str: Код `length` длины c заглавными буквами.
    """
    if length <= 0:
        msg = 'Длина должна быть больше 0.'
        raise ValueError(msg)
    return str(uuid.uuid4()).replace('-', '')[:length].upper()
