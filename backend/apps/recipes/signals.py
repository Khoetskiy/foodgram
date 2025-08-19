import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.recipes.models import Recipe
from apps.recipes.services import _get_old_image_path, archive_file_by_path

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Recipe, dispatch_uid='move_files_to_archive')
def move_images_to_archive(sender, instance, **kwargs):
    """
    Перемещает фотографию удаленного рецепта в архив.

    Args:
        sender (Model): Класс модели, отправившей сигнал.
        instance (Recipe): Экземпляр модели, который был удалён.

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
