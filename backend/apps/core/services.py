from django.urls import reverse

from apps.core.utils import render_html_list_block


def get_objects(
    items: list,
    admin_url: str,
    item_args,
    display_value,
    title: str,
) -> str:
    """
    Возвращает HTML-блок со списком объектов с админ-ссылками.

    Для каждого объекта создаётся ссылка на страницу редактирования в админке.
    Если объектов нет, возвращается символ '—'.

    Args:
        items (list): Список объектов, например obj.items.all().
        admin_url (str): Имя URL для reverse.
        item_args: Функция (lambda), принимающая объект и возвращающая
                                        список аргументов для reverse.
        display_value: Функция (lambda), принимающая объект и возвращающая
                                            отображаемое значение (текст).
        title (str): Заголовок раскрывающегося блока.

    Returns:
        str: HTML-блок со ссылками на объекты или '—'.
    """
    if not items:
        return '—'

    args_list = [
        (
            reverse(admin_url, args=item_args(item)),
            display_value(item),
        )
        for item in items
    ]
    return render_html_list_block(args_list, title)
