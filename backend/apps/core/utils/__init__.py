# ruff: noqa: TID252
"""
Пакет `utils` — набор вспомогательных функций, используемых в проекте.

Импортируя из `utils`, можно сразу использовать нужные функции,
это облегчает импорт и скрывает внутреннюю структуру `utils` от внешнего кода.

Пример:
    from utils import translate_text, create_slug

Модули:
    - files.py      — работа с файлами
    - html.py       — работа с HTML
    - slug.py       — создание и обработка slug'ов
    - text.py       — перевод, нормализация и обрезка текста
    - time.py       — преобразование и форматирование дат и времени
"""

from .files import (
    decode_base64_image,
    generate_unique_filename,
    get_safe_extension,
)
from .html import render_html_list_block
from .slug import append_number_to_slug, create_slug, parse_slug_number
from .text import capitalize_name, is_cyrillic, translate_text, truncate_text
from .time import format_duration_time

__all__ = [
    'append_number_to_slug',
    'capitalize_name',
    'create_slug',
    'decode_base64_image',
    'format_duration_time',
    'generate_unique_filename',
    'get_safe_extension',
    'is_cyrillic',
    'parse_slug_number',
    'render_html_list_block',
    'translate_text',
    'truncate_text',
]
