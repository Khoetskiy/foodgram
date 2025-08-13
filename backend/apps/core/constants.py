# --- Ограничения для полей модели Recipe ---
RECIPE_NAME_MAX_LENGTH = 256
MIN_COOK_TIME = 1  # в минутах
MAX_COOK_TIME = 60 * 12
RECIPE_SHORT_CODE_MAX_LENGTH = 8

# --- Ограничения для полей модели Tag ---
TAG_NAME_MAX_LENGTH = TAG_SLUG_MAX_LENGTH = 32

# --- Ограничения для полей модели Ingredient ---
INGREDIENT_NAME_MAX_LENGTH = 128
INGREDIENT_NAME_MIN_LENGTH = 3
MIN_AMOUNT_INGREDIENTS = 1
MAX_AMOUNT_INGREDIENTS = 1000

# --- Ограничения для полей модели MeasurementUnit ---
MEASUREMENTUNIT_MAX_NAME_LENGTH = 64

# --- Ограничения для полей модели CustomUser ---
USERNAME_LENGTH = FIRST_NAME_LENGTH = LAST_NAME_LENGTH = 150
USERNAME_MIN_LENGTH = FIRST_NAME_MIN_LENGTH = LAST_NAME_MIN_LENGTH = 4
USERNAME_VALIDATION_REGEX = r'^\w+$'
NAME_VALIDATION_REGEX = r'^[A-Za-zА-Яа-яЁё]+$'
EMAIL_LENGTH = 254

# --- Настройки отображения текста ---
TEXT_TRUNCATE_LENGTH = TEXT_TRUNCATE_LENGTH_ADMIN = 50
TEXT_TRUNCATE_SUFFIX = '..'

# --- Настройки загрузки файлов ---
ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png')
DEFAULT_EXT = 'jpg'
MAX_SIZE_FILE: int = 5  # MB

# --- misc ---
MAX_ATTEMPTS = 1000
ARCHIVE_ROOT = 'archive'
UUID_FILENAME_LENGTH = 10
SHORT_LINK_PREFIX = 's'

# --- API ---
DISABLED_ACTIONS_DJOSER = [
    'activation',
    'resend_activation',
    'reset_password',
    'reset_password_confirm',
    'set_username',
    'reset_username',
    'reset_username_confirm',
]
PAGE_SIZE_PAGINATION = 10
MAX_PAGE_SIZE_PAGINATION = 50

# --- Help texts для моделей приложения users ---
CUSTOMUSER_USERNAME_HELP = (
    'Уникальное имя пользователя. '
    'Должно содержать только латинские буквы, цифры и подчёркивания. '
    f'Минимум {USERNAME_MIN_LENGTH} символов(а).'
)
CUSTOMUSER_EMAIL_HELP = (
    'Действующий и уникальный адрес электронной почты, используемый для входа.'
)
CUSTOMUSER_FIRSTNAME_HELP = (
    'Введите имя (только буквы кириллицы или латиницы).'
)
CUSTOMUSER_LASTNAME_HELP = (
    'Введите фамилию (только буквы кириллицы или латиницы).'
)
CUSTOMUSER_AVATAR_HELP = (
    f'Загрузите фото в формате {", ".join(ALLOWED_EXTENSIONS)}. '
    f'Максимальный размер: {MAX_SIZE_FILE}МБ.'
)

FAVORITE_USER_HELP = 'Пользователь, у которого есть список избранного.'

FAVORITEITEM_FAVORITE_HELP = (
    'Список избранного, к которому относится этот элемент.'
)
FAVORITEITEM_RECIPE_HELP = 'Рецепт, добавленный в избранное.'

SUBSCRIBE_USER_HELP = 'Пользователь, который подписывается.'
SUBSCRIBE_AUTHOR_HELP = 'Пользователь, на которого подписываются.'
