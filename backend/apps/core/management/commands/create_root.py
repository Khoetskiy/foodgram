from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание супер-пользователя'

    def handle(self, *args, **kwargs):
        username = 'root'
        email = 'root@mail.com'
        password = 'root'
        first_name = 'root'
        last_name = 'rooot'
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError as e:
            self.stderr.write(
                self.style.ERROR(
                    f'Ошибка: {e}Пользователь с такими данными уже существует!'
                )
            )
        except (ValueError, TypeError) as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка: {e}\nДанные некорректны!')
            )
        else:
            msg = 'Создан супер-пользователь с данными:'
            data = (
                f'username: {username}\nemail: {email}\npassword: {password}'
            )
            self.stdout.write(self.style.SUCCESS(msg))
            self.stdout.write(self.style.MIGRATE_LABEL(data))
