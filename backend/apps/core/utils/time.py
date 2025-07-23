def format_duration_time(minutes: int) -> str:
    """
    Преобразует количество минут в строку вида:
    - "45 мин."
    - "1 ч."
    - "1 ч. 30 мин."

    Args:
        minutes (int): Общее количество минут.

    Returns:
        str: Отформатированное строковое представление.
    """
    hour = 60
    if minutes < hour:
        return f'{minutes} мин.'
    hours = minutes // hour
    mins = minutes % hour
    if mins:
        return f'{hours} ч. {minutes} мин.'
    return f'{hours} ч.'
