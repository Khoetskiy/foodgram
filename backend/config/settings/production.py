from .base import *

if DEBUG:
    raise RuntimeError(
        'ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ: не запускайте с включенной отладкой в производственной среде!'
    )


# # Дополнительные настройки безопасности для продакшена
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_HSTS_SECONDS = 31536000  # 1 год
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# # Настройки CSRF для продакшена
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SAMESITE = 'Strict'
# # Настройки CORS для продакшена
# CORS_ALLOW_ALL_ORIGINS = False
# CORS_ALLOWED_ORIGINS = [
#     origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()
# ]
