import os

from decouple import config

environment = config('DJANGO_ENVIRONMENT', default='development')

if environment == 'production':
    from .production import *
elif environment == 'testing':
    from .testing import *
else:
    from .development import *


if os.environ.get('RUN_MAIN') == 'true':
    MAGENTA = '\033[95m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

    msg = (
        f'Django запущен в режиме: {GREEN}{environment}{RESET}\n'
        f'DEBUG режим: {YELLOW}{DEBUG}{RESET}\n'
        f'Разрешенные хосты: {CYAN}{ALLOWED_HOSTS}{RESET}'
    )
    border = '=' * 50
    print(f'\n{MAGENTA}{border}{RESET}')
    print(msg)
    print(f'{MAGENTA}{border}{RESET}\n')
