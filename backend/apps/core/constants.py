# --- Ограничения для полей модели Recipe ---
RECIPE_NAME_MAX_LENGTH = 256
MIN_COOK_TIME = 1  # в минутах
MAX_COOK_TIME = 60 * 12

# --- Ограничения для полей модели Tag ---
TAG_NAME_MAX_LENGTH = TAG_SLUG_MAX_LENGTH = 32

# --- Ограничения для полей модели Ingredient ---
INGREDIENT_NAME_MAX_LENGTH = 128
INGREDIENT_NAME_MIN_LENGTH = 3
MIN_AMOUNT_INGREDIENTS = 1

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

# --- Для core/utils ---
MAX_ATTEMPTS = 1000  # Для генерации slug ---
ARCHIVE_ROOT = 'archive'
UUID_FILENAME_LENGTH = 10
