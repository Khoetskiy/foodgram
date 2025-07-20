from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.utils.text import get_valid_filename

from apps.core.constants import MAX_SIZE_FILE


class CantBeNameFileError(Exception):
    """"""

    def __init__(self, filename):
        super().__init__(
            f'Недопустимое имя файла: "{filename}". '
            'Имя файла содержит недопустимые символы.'
        )


class ValidateSizeError(Exception):
    def __init__(self, max_size):
        super().__init__(f'Размер файла не должен превышать {max_size}MB')


def validate_safe_filename(file: str) -> None:
    """Валидатор для проверки безопасности имени файла."""
    try:
        get_valid_filename(file)
    except SuspiciousFileOperation as e:
        raise CantBeNameFileError(file) from e


def validate_file_size(file) -> None:
    max_size = MAX_SIZE_FILE * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f'Размер файла не должен превышать {MAX_SIZE_FILE}MB'
        )
