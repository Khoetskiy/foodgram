import logging

from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.recipes.models import Recipe, Tag
from apps.recipes.services import (
    _get_old_image_path,
    archive_file_by_path,
    generate_unique_slug,
)

logger = logging.getLogger(__name__)


# # FIXME: Убрать если в этом нет необходимости?
# @receiver(pre_save, sender=Tag, dispatch_uid='generate_tag_slug')
# def generate_tag_slug(sender, instance, **kwargs):
#     """
#     Генерирует уникальный slug для тега перед сохранением.

#     Если поле slug отсутствует или изменено имя,
#     генерируется новый slug на основе имени.
#     Используя `generate_unique_slug` для обеспечения уникальности.

#     Args:
#         sender (Model): Класс модели, отправившей сигнал.
#         instance (Tag): Экземпляр модели.
#         **kwargs: Дополнительные аргументы.

#     Raises:
#         ValidationError: Если не удалось сгенерировать slug.
#     """

#     try:
#         existing = sender.objects.only('name').get(pk=instance.pk)
#         if not instance.slug or instance.name != existing.name:
#             instance.slug = generate_unique_slug(
#                 sender, instance.name, instance=instance, allow_unicode=True
#             )
#             logger.info(
#                 f'Сгенерирован slug: {instance.slug} для тега: {instance.name}'
#             )
#     except sender.DoesNotExist:
#         if instance.slug:  # Если пользователь сам заполнил slug
#             return
#         instance.slug = generate_unique_slug(
#             sender, instance.name, instance=instance
#         )
#         logger.info(f'Сгенерирован slug для нового тега: {instance.slug}')
#     except (ValueError, RuntimeError) as e:
#         message = f'Ошибка генерации slug для тега {instance.name}: {e!s}'
#         logger.exception('Ошибка генерации slug для тега')
#         raise ValidationError(message, code='error_create_slug') from e


@receiver(post_delete, sender=Recipe, dispatch_uid='move_files_to_archive')
def move_images_to_archive(sender, instance, **kwargs):
    """
    Перемещает фотографию удаленного рецепта в архив.

    Args:
        sender (Model): Класс модели, отправившей сигнал.
        instance (Recipe): Экземпляр модели, который был удалён.
        **kwargs: Дополнительные аргументы.

    Raises:
        IndexError: Ошибка структуры пути.
        shutil.Error: Ошибка при перемещении файла.
        OSError: Ошибка файловой системы.
    """
    if instance.image:
        archive_file_by_path(instance.image.path)


@receiver(pre_save, sender=Recipe, dispatch_uid='cache_old_image_path')
def cache_old_image_path(sender, instance, **kwargs):
    """
    Сохраняет путь к старой фотографии, если она будет заменена.

    Перед сохранением объекта проверяется, была ли изменена фотография.
    Если да - путь к старой фотографии сохраняется для последующей архивации.

    Args:
        sender (Model): Модель, отправившая сигнал.
        instance (Recipe): Экземпляр рецепта.
        **kwargs: Дополнительные аргументы.
    """
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_file = old_instance.image
    new_file = instance.image

    if (old_file and new_file) and old_file != new_file:
        _get_old_image_path()[instance.pk] = old_file.path


@receiver(post_save, sender=Recipe, dispatch_uid='archive_replaced_image')
def archive_replaced_image(sender, instance, **kwargs):
    """
    Перемещает старую фотографию в архив, если она была заменена.

    Args:
        sender (Model): Модель, отправившая сигнал.
        instance (Recipe): Экземпляр рецепта.

    Raises:
        IndexError: Ошибка структуры пути.
        shutil.Error: Ошибка при перемещении файла.
        OSError: Ошибка файловой системы.
    """
    old_path = _get_old_image_path().pop(instance.pk, None)
    if old_path:
        archive_file_by_path(old_path)


# @receiver(pre_save, sender=Recipe, dispatch_uid='save_recipe_image')
# def save_recipe_image(sender, instance, **kwargs):
#     """
#     Временно удаляет изображение, чтобы сохранить Recipe и получить pk.

#     При создании сохраняет экземпляр без изображения, чтобы получить pk,
#     затем восстанавливает изображение для корректного пути сохранения.

#     Args:
#         sender (Model): Модель, отправившая сигнал.
#         instance (Recipe): Экземпляр рецепта.
#     """
#     if not instance.pk and instance.image:
#         image = instance.image
#         instance.image = None
#         instance.save()
#         instance.image = image
