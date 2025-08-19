from django.utils.html import format_html, format_html_join


def render_html_list_block(args_list: list, title: str) -> str:
    """
    Рендерит HTML-список c раскрывающимся блоком.

    Args:
        args_list: (list) список объектов.
        title (str): имя блока.

    Returns:
        str: HTML-код c раскрывающимся списком.
    """
    html_list = format_html_join(
        '',
        '<li><a href="{}">{}</a></li>',
        args_list,
    )
    return format_html(
        """
        <details>
          <summary style="cursor: pointer; color: #0645AD">
            {}
          </summary>
            <ul style="margin: 4px 0 0 16px;">{}</ul>
        </detail>
        """,
        title,
        html_list,
    )
