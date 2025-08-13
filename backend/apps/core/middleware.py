from django.contrib import messages
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from apps.core.exceptions import ProjectError


class ProjectExceptionMiddleware(MiddlewareMixin):
    """Перехватывает исключения ProjectError в админке."""

    def process_exception(self, request, exception):
        if not isinstance(exception, ProjectError):
            return None

        if request.path.startswith('/admin/'):
            messages.error(request, str(exception))
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))

        return None
