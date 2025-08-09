import logging
import shutil
import threading

from os.path import relpath
from pathlib import Path

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from apps.core.constants import (
    ARCHIVE_ROOT,
    MAX_ATTEMPTS,
    RECIPE_SHORT_CODE_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from apps.core.exceptions import SlugGenerationError
from apps.core.utils.files import generate_unique_filename, get_safe_extension
from apps.core.utils.slug import (
    append_number_to_slug,
    create_slug,
    parse_slug_number,
)
from apps.core.utils.text import generate_short_code
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
    Генерирует уникальный slug для значения поля, c учётом базы данных.

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
        Путь вида `recipes/user_<user_id>/<recipe_id>/<uuid>.<ext>`
    """
    ext = get_safe_extension(filename)
    new_filename = generate_unique_filename(ext)
    return Path('recipes') / f'user_{instance.author.id}' / new_filename


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

    - Сохраняет относительную структуру пути относительно MEDIA_ROOT.
    - Если файл отсутствует, записывает предупреждение в лог.
    - При ошибках перемещения или создания директорий логирует исключения.

    Args:
        old_path (str): Абсолютный путь к файлу, который нужно архивировать.

    Raises:
        IndexError: Ошибка структуры пути.
        shutil.Error: Ошибка при перемещении файла.
        OSError: Ошибка файловой системы.
    """
    if not Path(old_path).is_file():
        logger.warning('Файл для архивирования не найден: %s', old_path)
        return

    try:
        relative_path = relpath(old_path, MEDIA_ROOT)
        archive_root = Path(MEDIA_ROOT) / Path(ARCHIVE_ROOT)
        new_path = archive_root / relative_path

        Path(new_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(old_path, new_path)
        logger.info('Файл "%s" перемещен в архив', relative_path)
    except IndexError:
        logger.exception('Ошибка структуры пути при архивировании')
    except shutil.Error:
        logger.exception('Ошибка перемещения файла')
    except OSError:
        logger.exception('Ошибка файловой системы')


def create_recipe_ingredients(recipe, ingredients_data: list[dict]) -> None:
    """
    Создает связи RecipeIngredient для рецепта.

    Args:
        recipe (Recipe): Сохраненный рецепт.
        ingredients_data (list[dict]): Список ингредиентов.
    """
    from apps.recipes.models import RecipeIngredient  # Иначе цикличный импорт

    RecipeIngredient.objects.bulk_create(
        [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount'],
            )
            for ingredient_data in ingredients_data
        ]
    )


def generate_unique_short_code(
    model_cls,
    field_name: str = 'short_code',
    length: int = RECIPE_SHORT_CODE_MAX_LENGTH,
    max_attempts: int = MAX_ATTEMPTS,
) -> str:
    """
    Генерирует код, проверяя уникальность в базе данных.

    После `max_attempts` попыток увеличивает длину на 1.

    Args:
        model_cls (Model): Класс модели
        field_name (str): Поле модели
        length (int): Длина уникального кода
        max_attempts (int): Количество попыток создания уникального кода

    Returns:
        str: Уникальный код
    """
    for _ in range(max_attempts):
        code = generate_short_code(length)
        if not model_cls.objects.filter(**{field_name: code}).exists():
            return code
    return generate_unique_short_code(
        model_cls, field_name, length + 1, max_attempts
    )


def get_txt_in_response(
    ingredients_summary: list[dict], filename: str = 'shopping_cart.txt'
) -> HttpResponse:
    """
    Создаёт txt-файл списка покупок на основе агрегированных ингредиентов.

    Args:
        ingredients_summary (list[dict]): список ингредиентов c полями:
        - 'ingredient__name'
        - 'ingredient__measurement_unit__name'
        - 'amount'
        filename (str): имя файла для скачивания

    Returns:
        HttpResponse: ответ c файлом для скачивания
    """

    lines = []
    lines.append('Список покупок')
    lines.append('=' * 50)
    lines.append(
        f'{"Ингредиент".ljust(28)} | '
        f'{"Ед. изм.".ljust(8)} | {"Кол-во".rjust(7)}'
    )
    lines.append('-' * 50)

    for item in ingredients_summary:
        name = item['ingredient__name']
        unit = item['ingredient__measurement_unit__name']
        amount = str(item['amount'])

        lines.append(f'{name.ljust(28)} | {unit.ljust(8)} | {amount.rjust(7)}')

    content = '\n'.join(lines)

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def manage_user_relation_object(
    model,
    relation_filter: dict,
    related_obj,
    related_field_name: str,
    serializer_class,
    serializer_context: dict,
    already_exists_message: str = 'Объект уже добавлен',
    not_found_message: str = 'Объект не найден',
):
    """
    Универсальная функция для управления связями пользователя c объектами.

    Args:
        model (Model): модель, связующая user и объект.
        relation_filter (dict): параметры фильтрации.
        related_obj (Model): объект, c которым создаётся или удаляется связь.
        related_field_name (str): имя поля в модели.
        serializer_class: сериализатор, который возвращается при POST-запросе.
        serializer_context (dict): контекст сериализатора.
        already_exists_message (str): сообщение, если объект уже добавлен.
        not_found_message (str): сообщение, если объект не найден.

    Returns:
        handler: функция-обработчик запроса.
    """

    def handler(request):
        filter_kwargs = {**relation_filter, related_field_name: related_obj}

        if request.method == 'POST':
            if model.objects.filter(**filter_kwargs).exists():
                return Response(
                    {'errors': already_exists_message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.create(**filter_kwargs)
            serializer = serializer_class(
                related_obj, context=serializer_context
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            deleted, _ = model.objects.filter(**filter_kwargs).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': not_found_message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return handler
