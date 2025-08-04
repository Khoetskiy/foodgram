from rest_framework.pagination import PageNumberPagination

from apps.core.constants import MAX_PAGE_SIZE_PAGINATION, PAGE_SIZE_PAGINATION


class CustomPageNumberPagination(PageNumberPagination):
    """Пагинатор, позволяющий пользователю задавать лимит на странице."""

    page_size = PAGE_SIZE_PAGINATION
    max_page_size = MAX_PAGE_SIZE_PAGINATION
    page_size_query_param = 'limit'
