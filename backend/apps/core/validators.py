from django.core.exceptions import SuspiciousFileOperation
from django.utils.text import get_valid_filename

from apps.core.constants import MAX_SIZE_FILE
from apps.core.exceptions import CantBeNameFileError, ValidateSizeError


def validate_safe_filename(file) -> None:
    """
    Проверяет имя файла на допустимость.

    Args:
        file (File): Загруженный файл, переданный через ImageField.

    Raises:
        CantBeNameFileError: Если имя файла содержит недопустимые символы.
    """
    try:
        get_valid_filename(file.name)
    except SuspiciousFileOperation as e:
        raise CantBeNameFileError(file) from e


def validate_file_size(file, max_size_mb: int = MAX_SIZE_FILE) -> None:
    """
    Проверяет, не превышает ли файл максимальный допустимый размер.

    Args:
        file (File): Загруженный файл, переданный через ImageField.
        max_size_mb (int): максимальный размер в мегабайтах.

    Raises:
        ValidationError: Если файл больше допустимого размера.
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidateSizeError(max_size=max_size_mb)
