# ruff: noqa
# flake8: noqa
from .base import *


INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'web',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    *REST_FRAMEWORK.get('DEFAULT_RENDERER_CLASSES', []),
    'rest_framework.renderers.BrowsableAPIRenderer',
]

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework.authentication.SessionAuthentication',
]
