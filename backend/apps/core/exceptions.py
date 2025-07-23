class CantBeNameFileError(Exception):
    """
    Исключение при недопустимом имени файла.

    Args:
        filename (str): Имя файла.
    """

    def __init__(self, filename: str):
        super().__init__(
            f'Недопустимое имя файла: "{filename}". '
            'Имя файла содержит недопустимые символы.'
        )


class ValidateSizeError(Exception):
    """
    Исключение при превышении максимального размера файла.

    Args:
        max_size (int): Максимально допустимый размер файла в мегабайтах.
    """

    def __init__(self, max_size: int):
        super().__init__(f'Размер файла не должен превышать {max_size}MB.')


class TranslationError(Exception):
    """
    Исключение при ошибке перевода с помощью внешнего сервиса.

    Args:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str):
        super().__init__(
            f'Ошибка перевода: {message}' if message else 'Ошибка перевода.'
        )


class SlugGenerationError(Exception):
    """
    Исключение при ошибке генерации slug.

    Args:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str):
        super().__init__(message)
