from datetime import timedelta
from pathlib import Path

from decouple import Csv, config
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent.parent

AUTH_USER_MODEL = 'users.CustomUser'

SECRET_KEY = config('DJANGO_SECRET_KEY', default=get_random_secret_key())

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv()
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',  # Отображается в админке
    'djoser',
    'django_filters',
    # 'rest_framework_simplejwt',
]

LOCAL_APPS = [
    'apps.core.apps.CoreConfig',
    'apps.users.apps.UsersConfig',
    'apps.recipes.apps.RecipesConfig',
    'apps.cart.apps.CartConfig',
    'apps.api.apps.ApiConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='django_db'),
            'USER': config('DB_USER', default='django_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru-Ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


Path(BASE_DIR / 'logs').mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG'
            if config('DEBUG', default=True, cast=bool)
            else 'WARNING',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'level': 'INFO',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG'
            if config('DEBUG', default=True, cast=bool)
            else 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


REST_FRAMEWORK = {
    'DEFAULT_RENDERS_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # веб-версия API
    ],  # FIXME: На проде отключить
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # IsAuthenticated
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',  # по умолчанию
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
}

DJOSER = {
    # 'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    # 'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    # 'ACTIVATION_URL': '#/activate/{uid}/{token}',
    # 'SEND_ACTIVATION_EMAIL': True,
    'SERIALIZERS': {
        # 'set_password': 'djoser.serializers.SetPasswordSerializer',
    },
    # 'PERMISSIONS': {
    #     'activation': ['rest_framework.permissions.AllowAny'],
    #     'password_reset': ['rest_framework.permissions.AllowAny'],
    #     'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
    #     'set_password': ['djoser.permissions.CurrentUserOrAdmin'],
    #     'username_reset': ['rest_framework.permissions.AllowAny'],
    #     'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
    #     'set_username': ['djoser.permissions.CurrentUserOrAdmin'],
    #     'user_create': ['rest_framework.permissions.AllowAny'],
    #     'user_delete': ['djoser.permissions.CurrentUserOrAdmin'],
    #     'user': ['djoser.permissions.CurrentUserOrAdmin'],
    #     'user_list': ['djoser.permissions.CurrentUserOrAdmin'],
    #     'token_create': ['rest_framework.permissions.AllowAny'],
    #     'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    # },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=90),  # HACK: временно
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': '',
    'AUDIENCE': None,
    'ISSUER': None,
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSerializer',
    'TOKEN_VERIFY_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenVerifySerializer',
    'TOKEN_BLACKLIST_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenBlacklistSerializer',
    'SLIDING_TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer',
    'SLIDING_TOKEN_REFRESH_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer',
}


# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 20,
#     'DEFAULT_RENDERER_CLASSES': [
#         'rest_framework.renderers.JSONRenderer',
#     ],
#     'DEFAULT_PARSER_CLASSES': [
#         'rest_framework.parsers.JSONParser',
#         'rest_framework.parsers.FormParser',
#         'rest_framework.parsers.MultiPartParser',
#     ],
#     'DEFAULT_THROTTLE_CLASSES': [
#         'rest_framework.throttling.AnonRateThrottle',
#         'rest_framework.throttling.UserRateThrottle',
#     ],
#     'DEFAULT_THROTTLE_RATES': {
#         'anon': '100/hour',
#         'user': '1000/hour',
#     },
# }


# # Настройки CORS
# CORS_ALLOWED_ORIGINS = [
#     origin.strip()
#     for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
#     if origin.strip()
# ]

# CORS_ALLOW_CREDENTIALS = True

# # Настройки CSRF
# CSRF_TRUSTED_ORIGINS = [
#     origin.strip()
#     for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
#     if origin.strip()
# ]

# # Настройки безопасности
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'

# # Настройки сессий
# SESSION_COOKIE_SECURE = not DEBUG
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_AGE = 86400  # 24 часа

# # Настройки CSRF куки
# CSRF_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_HTTPONLY = True


# # Настройки электронной почты
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.environ.get(
#     'DEFAULT_FROM_EMAIL', 'noreply@example.com'
# )
