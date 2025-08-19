def format_duration_time(minutes: int) -> str:
    """
    Преобразует количество минут в строку.

    Args:
        minutes (int): Общее количество минут.

    Returns:
        str: Отформатированное строковое представление, вида:
                                                        - "45 мин."
                                                        - "1 ч."
                                                        - "1 ч. 30 мин."
    """
    hour = 60
    hours = minutes // hour
    mins = minutes % hour

    if hours and mins:
        return f'{hours} ч. {mins} мин.'
    if hours:
        return f'{hours} ч.'
    return f'{mins} мин.'
