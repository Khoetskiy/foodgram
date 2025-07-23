import logging
import shutil
import threading

from os.path import relpath
from pathlib import Path

from apps.core.constants import ARCHIVE_ROOT, MAX_ATTEMPTS, TAG_SLUG_MAX_LENGTH
from apps.core.exceptions import SlugGenerationError
from apps.core.utils.files import generate_unique_filename, get_safe_extension
from apps.core.utils.slug import (
    append_number_to_slug,
    create_slug,
    parse_slug_number,
)
from config.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)

_local = threading.local()


def generate_unique_slug(
    model_class,
    field_value: str,
    instance=None,
    allow_unicode: bool = False,
    max_attempts: int = MAX_ATTEMPTS,
    max_length_slug: int = TAG_SLUG_MAX_LENGTH,
) -> str:
    """
    Генерирует уникальный slug для значения поля, с учётом базы данных.

    Args:
        field_value (str): Значение поля для slug.
        model_class: Класс модели.
        instance: Экземпляр модели для исключения при проверке уникальности.
        allow_unicode (bool): Разрешает использование Unicode-символов.
        max_length_slug (int): Максимальная длина slug.

    Returns:
        str: Уникальный slug.

    Raises:
        SlugGenerationError: Если slug превышает длину.
        RuntimeError: Если не найден уникальный slug после MAX_ATTEMPTS.
    """
    slug = create_slug(field_value, allow_unicode)[:max_length_slug]
    base_slug, start_count = parse_slug_number(slug)

    qs = model_class.objects.filter(slug__startswith=base_slug)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    existing_slugs = set(qs.values_list('slug', flat=True))

    if slug not in existing_slugs:
        return slug

    count = start_count or 2

    while count <= max_attempts:
        new_slug = append_number_to_slug(base_slug, count)
        if new_slug not in existing_slugs:
            if len(new_slug) > max_length_slug:
                msg = (
                    'Сгенерированный slug превышает максимальную длину '
                    f'{max_length_slug} символов'
                )
                raise SlugGenerationError(msg)
            return new_slug
        count += 1

    msg = (
        f'Не удалось найти уникальный slug после {max_attempts} '
        f'попыток для "{field_value}"'
    )
    raise RuntimeError(msg)


def recipe_image_upload_path(instance, filename: str) -> Path:
    """
    Возвращает путь для загрузки фотографии рецепта внутри MEDIA_ROOT:

    Args:
        instance: объект модели Recipe
        filename (str): оригинальное имя файла

    Returns:
        Путь вида 'recipes/user_<user_id>/<recipe_id>/<uuid>.<ext>'
    """
    ext: str = get_safe_extension(filename)
    new_filename: str = generate_unique_filename(ext)

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
        logger.info(f'Файл "{relative_path}" перемещен в архив')
    except IndexError:
        logger.exception('Ошибка структуры пути при архивировании')
    except shutil.Error:
        logger.exception('Ошибка перемещения файла')
    except OSError:
        logger.exception('Ошибка файловой системы')
