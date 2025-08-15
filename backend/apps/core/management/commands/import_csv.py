import csv

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import IntegrityError

from apps.recipes.models import (
    Ingredient,
    MeasurementUnit,
    Recipe,
    RecipeIngredient,
    Tag,
)
from apps.users.models import Cart, Favorite, Subscribe

User = get_user_model()

MODEL_CLASS_MAP = {
    'user': User,
    'measurementunit': MeasurementUnit,
    'ingredient': Ingredient,
    'recipe': Recipe,
    'tag': Tag,
    'recipeingredient': RecipeIngredient,
    'recipetag': Recipe.tags.through,
    'cart': Cart,
    'favorite': Favorite,
    'subscribe': Subscribe,
}


class Command(BaseCommand):
    help = 'Загрузка данных в БД из CSV в зависимости от модели.'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='Имя модели')
        parser.add_argument('file_path', type=str, help='Путь к CSV-файлу')

    def handle(self, *args, **kwargs):
        model_name = kwargs['model_name']
        file_path = kwargs['file_path']

        if model_name not in MODEL_CLASS_MAP:
            self.stderr.write(
                self.style.ERROR(
                    f'Импорт для модели "{model_name.capitalize()}" '
                    'не поддерживается!'
                )
            )
            return

        try:
            with open(file_path, encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                model_class = MODEL_CLASS_MAP[model_name]
                self.import_data(reader, model_class)

        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(f'Файл "{file_path}" не найден')
            )
        except csv.Error as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при чтении CSV: {e}'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Импорт данных для модели {model_name} прошел успешно!'
                )
            )

    def import_data(self, reader: csv.DictReader, modelclass):
        """Импортирует данные из CSV в указанную модель базы данных."""
        bulk_objects = []
        for row in reader:
            filtered_data = self.convert_data_types(row)

            try:
                obj = modelclass(**filtered_data)
                bulk_objects.append(obj)
            except ValueError:
                self.stderr.write(
                    self.style.WARNING(f'Некорректные данные в строке: {row}')
                )

        try:
            if bulk_objects:
                modelclass.objects.bulk_create(bulk_objects)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно загружено {len(bulk_objects)} '
                        f'объектов(а) для модели "{modelclass.__name__}".'
                    )
                )
            else:
                self.stdout.write(
                    self.style.NOTICE('Не было загружено ни одного объекта.')
                )
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f'Ошибка IntegrityError: {e}.'))
            self.stderr.write(self.style.ERROR(f'Строка: {row}.'))

    def convert_data_types(self, row: dict) -> dict:
        """Преобразует данные из CSV в нужные типы."""
        return {
            field: int(value) if value.isdigit() else value
            for field, value in row.items()
        }
