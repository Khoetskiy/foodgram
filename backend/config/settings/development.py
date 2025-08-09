# ruff: noqa
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

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    *REST_FRAMEWORK.get('DEFAULT_RENDERER_CLASSES', []),
    'rest_framework.renderers.BrowsableAPIRenderer',
]

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework.authentication.SessionAuthentication',
]
