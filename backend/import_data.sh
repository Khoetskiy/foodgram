#!/bin/bash

set -e
set -u

CSV_DIR="../data/csv"
MEDIA_ROOT="media"
IMAGE_SRC="$CSV_DIR/default.png"
IMAGE_DEST="$MEDIA_ROOT/recipes/images/default.png"

echo "Проверка окружения..."

if [ ! -f "manage.py" ]; then
    echo "Ошибка: manage.py не найден. Запустите скрипт из корня Django проекта"
    exit 1
fi

if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo "Предупреждение: виртуальное окружение не активировано"
    exit 1
fi

echo "Создаю супер-пользователя..."

if python manage.py create_root; then
    echo "✓ Суперпользователь создан"
else
    echo "Предупреждение: не удалось создать суперпользователя"
fi

COMMANDS=(
    "user $CSV_DIR/users.csv"
    "measurementunit $CSV_DIR/measurement_units.csv"
    "ingredient $CSV_DIR/ingredients.csv"
    "tag $CSV_DIR/tags.csv"
    "recipe $CSV_DIR/recipes.csv"
    "recipeingredient $CSV_DIR/recipe_ingredients.csv"
    "recipetag $CSV_DIR/recipe_tags.csv"
    "cart $CSV_DIR/carts.csv"
    "cartitem $CSV_DIR/cart_items.csv"
    "favorite $CSV_DIR/favorites.csv"
    "favoriteitem $CSV_DIR/favorite_items.csv"
)

echo "Проверка CSV файлов..."
for cmd in "${COMMANDS[@]}"; do
    filename=$(echo $cmd | awk '{print $2}')
    if [ ! -f "$filename" ]; then
        echo "× Ошибка: файл $filename не найден"
        exit 1
    fi
    echo "✓ $filename найден"
done

echo "Создание директории для изображений, если она не существует..."
mkdir -p "$MEDIA_ROOT/recipes/images"

if [ -f "$IMAGE_SRC" ]; then
    cp "$IMAGE_SRC" "$IMAGE_DEST"
    echo "✓ Изображение скопировано: $IMAGE_DEST"
else
    echo "× Предупреждение: Файл $IMAGE_SRC не найден. Импорт рецептов может завершиться с ошибкой."
fi

echo "Начало импорта данных..."
total_commands=${#COMMANDS[@]}
current_command=0

for cmd in "${COMMANDS[@]}"; do
    current_command=$((current_command + 1))
    model_name=$(echo $cmd | awk '{print $1}')
    full_cmd="python manage.py import_csv $cmd"

    echo "[$current_command/$total_commands] Импорт $model_name..."
    echo "Выполняется: $full_cmd"

    if ! $full_cmd; then
        echo "Ошибка при выполнении команды для $model_name. Импорт остановлен."
        exit 1
    fi

    echo "✓ $model_name импортирован успешно"
done

echo "✓ Импорт всех данных завершен успешно!"

echo "Выполнение скрипта завершено успешно!"
