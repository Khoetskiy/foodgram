# ruff: noqa

from .base import *

if DEBUG:
    raise RuntimeError(
        'ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: '
        'не запускайте с включенной отладкой в производственной среде!'
    )

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv(),
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8080',
    cast=Csv(),
)

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
