import logging
import re
import shutil
import threading

from os.path import relpath
from pathlib import Path
from uuid import uuid4

from django.utils.text import slugify

from apps.core.constants import (
    ALLOWED_EXTENSIONS,
    ARCHIVE_ROOT,
    DEFAULT_EXT,
    MAX_ATTEMPTS,
    TAG_SLUG_MAX_LENGTH,
    TEXT_TRUNCATE_LENGTH,
    TEXT_TRUNCATE_SUFFIX,
    UUID_FILENAME_LENGTH,
)
from config.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)

_local = threading.local()


def truncate_text(
    text: str,
    length: int = TEXT_TRUNCATE_LENGTH,
    suffix: str = TEXT_TRUNCATE_SUFFIX,
) -> str:
    """
    Обрезает текст и добавляет суффикс, если он превышает указанную длину

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


def generate_unique_slug(
    model_class,
    field_value: str,
    instance=None,
    allow_unicode: bool = False,
) -> str:
    """
    Генерирует уникальный slug на основе значения поля.

    Args:
        model_class: Класс модели.
        field_value (str): Значение поля для slug.
        instance: Экземпляр модели для исключения при проверке уникальности.
        allow_unicode (bool): Разрешает использование Unicode-символов.

    Returns:
        str: уникальный slug.

    Raises:
        ValueError: Если field_value пустое.
        RuntimeError: Если не удалось найти уникальный slug.
    """
    if not field_value:
        msg = '"field_value" не может быть пустым'
        raise ValueError(msg)

    base_slug = slugify(field_value, allow_unicode=allow_unicode)[
        :TAG_SLUG_MAX_LENGTH
    ]
    if not base_slug:
        msg = 'Не удалось сгенерировать slug из переданного значения'
        raise ValueError(msg)

    match = re.match(r'^(.*?)-(\d+)$', base_slug)
    if match:
        base_slug, last_number = match.groups()
        start_count = int(last_number) + 1
    else:
        start_count = 1

    qs = model_class.objects.filter(slug__startswith=base_slug)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    existing_slugs = set(qs.values_list('slug', flat=True))

    slug = base_slug
    count = start_count
    while count <= MAX_ATTEMPTS:
        if slug not in existing_slugs:
            if len(slug) > TAG_SLUG_MAX_LENGTH:
                msg = (
                    'Сгенерированный slug превышает максимальную длину '
                    '{TAG_SLUG_MAX_LENGTH} символов'
                )
                raise ValueError(msg)
            return slug
        slug = f'{base_slug}-{count}'
        count += 1
    msg = (
        f'Не удалось найти уникальный slug после {MAX_ATTEMPTS} '
        'попыток для "{field_value}"'
    )
    raise RuntimeError(msg)


def _get_safe_extension(filename: str) -> str:
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
        logger.warning(
            f'Файл {filename} без расширения или недопустимое расширение'
        )
        return f'.{DEFAULT_EXT}'
    return ext.lower()


def _generate_unique_filename(ext: str) -> str:
    """
    Генерирует уникальное имя файла.

    Args:
        ext (str): расширение файла.

    Returns:
        str: уникальное название файла.
    """
    return f'{uuid4().hex[:UUID_FILENAME_LENGTH]}{ext}'


def recipe_image_upload_path(instance, filename: str) -> Path:
    """
    Возвращает путь для загрузки фотографии рецепта внутри MEDIA_ROOT:

    Args:
        instance: объект модели Recipe
        filename (str): оригинальное имя файла

    Returns:
        Путь вида 'recipes/user_<user_id>/<recipe_id>/<uuid>.<ext>'
    """
    ext: str = _get_safe_extension(filename)
    new_filename: str = _generate_unique_filename(ext)

    return (
        Path('recipes')
        / f'user_{instance.author.id}'
        / f'recipe_{instance.id if instance.id else "new"}'
        / new_filename
    )


def _get_old_image_path() -> dict:
    """
    Возвращает потокобезопасное хранилище старых путей фотографий.

    Используется для временного кеширования старых путей фотографий рецептов
    между сигналами pre_save и post_save.
    Хранение реализовано через threading.local,
    чтобы избежать конфликтов при параллельных запросах.

    Returns:
        dict: Словарь, в котором ключами являются ID объектов Recipe,
        a значениями - пути к фотографиям.
    """
    if not hasattr(_local, 'old_image_path'):
        _local.old_image_path = {}
    return _local.old_image_path


def archive_file_by_path(old_path: str) -> None:
    """
    Перемещает файл по указанному пути в директорию архива.

    Сохраняет относительную структуру пути относительно MEDIA_ROOT.
    Если файл отсутствует, записывает предупреждение в лог.
    При ошибках перемещения или создания директорий логирует исключения.

    Args:
        old_path (str): Абсолютный путь к файлу, который нужно архивировать.

    Raises:
        IndexError: Ошибка структуры пути.
        shutil.Error: Ошибка при перемещении файла.
        OSError: Ошибка файловой системы.
    """
    if not Path(old_path).is_file():
        logger.warning(f'Файл для архивирования не найден: {old_path}')
        return

    try:
        relative_path = relpath(old_path, MEDIA_ROOT)
        archive_root = MEDIA_ROOT / ARCHIVE_ROOT
        new_path = archive_root / relative_path

        Path(new_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(old_path, new_path)
        logger.info(f'Файл {relative_path} перемещен в архив')
    except IndexError:
        logger.exception('Ошибка структуры пути при архивировании')
    except shutil.Error:
        logger.exception('Ошибка перемещения файла')
    except OSError:
        logger.exception('Ошибка файловой системы')
