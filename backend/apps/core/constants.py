# Ограничения для полей модели Recipe
RECIPE_NAME_MAX_LENGTH = 256
MIN_COOK_TIME = 1  # в минутах
MAX_COOK_TIME = 60 * 12

# Ограничения для полей модели Tag
TAG_NAME_MAX_LENGTH = TAG_SLUG_MAX_LENGTH = 32

# Ограничения для полей модели Ingredient
INGREDIENT_NAME_MAX_LENGTH = 128
INGREDIENT_NAME_MIN_LENGTH = 3

# Ограничения для полей модели MeasurementUnit
MEASUREMENTUNIT_MAX_NAME_LENGTH = 64

# Настройки отображения текста
TEXT_TRUNCATE_LENGTH = TEXT_TRUNCATE_LENGTH_ADMIN = 50
TEXT_TRUNCATE_SUFFIX = '..'

# Настройки загрузки файлов
ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png')
DEFAULT_EXT = 'jpg'
MAX_SIZE_FILE = 5  # MB

# Для core/utils
MAX_ATTEMPTS = 1000  # Для генерации slug
ARCHIVE_ROOT = 'archive'
UUID_FILENAME_LENGTH = 10
