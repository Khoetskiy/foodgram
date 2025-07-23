from django.core.exceptions import SuspiciousFileOperation
from django.utils.text import get_valid_filename

from apps.core.constants import MAX_SIZE_FILE
from apps.core.exceptions import CantBeNameFileError, ValidateSizeError


def validate_safe_filename(filename: str) -> None:
    """
    Проверяет имя файла на допустимость.

    Args:
        filename (str): Имя файла.

    Raises:
        CantBeNameFileError: Если имя файла содержит недопустимые символы.
    """
    try:
        get_valid_filename(filename)
    except SuspiciousFileOperation as e:
        raise CantBeNameFileError(filename) from e


def validate_file_size(file_size: int) -> None:
    """
    Проверяет размер файла.

    Args:
        file_size (int): Размер файла (в байтах).

    Raises:
        ValidateSizeError: Если размер файла превышает допустимый лимит.
    """
    max_size_bytes  = MAX_SIZE_FILE * 1024 * 1024
    if file_size > max_size_bytes :
        raise ValidateSizeError(max_size=MAX_SIZE_FILE)
