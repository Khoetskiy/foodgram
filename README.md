---
related:
tags:
created:
---
# Foodgram - Продуктовый помощник

[![CI/CD Workflow](https://github.com/Khoetskiy/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Khoetskiy/foodgram/actions/workflows/main.yml)

**Веб-сервис для публикации и обмена кулинарными рецептами**

Foodgram — это платформа, где пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на авторов. Сервис также позволяет создавать список покупок для выбранных блюд.

**Адрес сайта:** https://foodgram.servepics.com

# Содержание
- [Foodgram - Продуктовый помощник](#foodgram---продуктовый-помощник)
- [Содержание](#содержание)
  - [Основные возможности](#основные-возможности)
  - [API Endpoints](#api-endpoints)
    - [Основные маршруты:](#основные-маршруты)
  - [Технологии](#технологии)
    - [Backend:](#backend)
    - [DevOps:](#devops)
    - [Frontend:](#frontend)
  - [Локальный запуск в Docker](#локальный-запуск-в-docker)
    - [1. Клонирование репозитория](#1-клонирование-репозитория)
    - [2. Создание файла переменных окружения - `.env`](#2-создание-файла-переменных-окружения---env)
    - [3. Запуск контейнеров](#3-запуск-контейнеров)
    - [4. Настройка базы данных](#4-настройка-базы-данных)
    - [5. Доступ к приложению](#5-доступ-к-приложению)
  - [Деплой на сервер](#деплой-на-сервер)
    - [Подготовка сервера](#подготовка-сервера)
    - [Настройка GitHub Actions](#настройка-github-actions)
    - [Файлы для продакшена](#файлы-для-продакшена)
    - [Запуск на сервере](#запуск-на-сервере)
  - [Структура проекта](#структура-проекта)
  - [Скрипты управления](#скрипты-управления)
    - [Команды Django Management](#команды-django-management)
  - [Участие в разработке](#участие-в-разработке)
  - [Лицензия](#лицензия)
  - [Автор](#автор)
  - [Поддержка](#поддержка)


## Основные возможности

- **Публикация рецептов** с фотографиями и пошаговым описанием
- **Избранное** — сохранение понравившихся рецептов
- **Подписки** на интересных авторов
- **Список покупок** — автоматическое формирование списка ингредиентов
- **Теги** для категоризации рецептов (завтрак, обед, ужин)
- **Поиск и фильтрация** рецептов по различным критериям
- **Адаптивный дизайн** для всех устройств

## API Endpoints

### Основные маршруты:

```
GET    /api/recipes/          - Список рецептов
POST   /api/recipes/          - Создание рецепта
GET    /api/recipes/{id}/     - Получение рецепта
PATCH  /api/recipes/{id}/     - Обновление рецепта
DELETE /api/recipes/{id}/     - Удаление рецепта

GET    /api/users/            - Список пользователей
POST   /api/users/            - Регистрация
GET    /api/users/me/         - Текущий пользователь

GET    /api/tags/             - Список тегов
GET    /api/ingredients/      - Список ингредиентов
```

>**Полная документация API:** https://foodgram.servepics.com/api/docs/

## Технологии

### Backend:

![Python](https://img.shields.io/badge/Python-3.12.3-3776AB?style=for-the-badge&logo=python&logoColor=yellow) ![Django](https://img.shields.io/badge/Django-5.2.4-092E20?style=for-the-badge&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-3.16-ff1709?style=for-the-badge&logo=django&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![Djoser](https://img.shields.io/badge/Djoser-2.3.3-4CAF50?style=for-the-badge&logo=django&logoColor=white) ![Pillow](https://img.shields.io/badge/Pillow-11.3.0-FF6B6B?style=for-the-badge&logo=python&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-20.1.0+-00ADD8?style=for-the-badge&logo=gunicorn&logoColor=green)

### DevOps:

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

### Frontend:

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)


## Локальный запуск в Docker

> **Предварительные требования**:
>- Docker
>- Git

### 1. Клонирование репозитория

```bash
https://github.com/Khoetskiy/foodgram.git
cd foodgram
```

### 2. Создание файла переменных окружения - `.env`

Создайте файл `.env` в корне проекта:

```env
# Django settings
DJANGO_ENVIRONMENT=development
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain,your-ip-address
DJANGO_SECRET_KEY=your-secret-key-here
CSRF_TRUSTED_ORIGINS=your-domain-or-ip-address

# DB settings
USE_SQLITE=True
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432

# Gunicorn settings
GUNICORN_PORT=8080
```

### 3. Запуск контейнеров

```bash
sudo docker-compose up -d --build
sudo docker-compose ps
```

### 4. Настройка базы данных

При старте Docker для контейнера backend используется скрипт `entrypoint.sh`, он выполняет:
- Создание миграций
- Применение миграций
- Сбор статических файлов
- Старт Gunicorn

### 5. Доступ к приложению

- **Главная страница:** http://localhost
- **API документация:** http://localhost/api/docs/
- **Админ-панель:** http://localhost/admin/

## Деплой на сервер

### Подготовка сервера

1. **Подключение к серверу и установка зависимостей:**

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Создание директории проекта:**

```bash
mkdir foodgram && cd foodgram
```

### Настройка GitHub Actions

Добавьте следующие секреты в настройках репозитория GitHub:

| Секрет            | Описание                        |
| ----------------- | ------------------------------- |
| `DOCKERHUB_TOKEN` | Токен Docker Hub (можно пароль) |
| `DOCKER_USERNAME` | Логин Docker Hub                |
| `HOST`            | IP адрес сервера                |
| `KEY`             | Приватный SSH ключ              |
| `SSH_PASSPHRASE`  | Пароль от SSH ключа (если есть) |
| `USER`            | Имя пользователя на сервере     |
| `TELEGRAM_ID`     | ID аккаунта в телеграмм         |
| `TELEGRAM_TOKEN`  | Токен телеграмм-бота            |

### Файлы для продакшена

1. **docker-compose.production.yml:**

```yaml
volumes:
  pg_data:
  static:
  media:

services:
  db:
    container_name: foodgram-db
    image: postgres:15
    env_file:
      - .env
    volumes:
      - pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    restart: unless-stopped

  backend:
    container_name: foodgram-back
    image: your-dockerhub-username/foodgram_backend:latest
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
        restart: true
    volumes:
      - static:/app/collectstatic
      - media:/app/media
    restart: unless-stopped

  frontend:
    image: your-dockerhub-username/foodgram_frontend:latest
    container_name: foodgram-frontend
    volumes:
      - static:/app/result_build
    depends_on:
      - backend

  nginx:
    image: your-dockerhub-username/foodgram_nginx:latest
    container_name: foodgram-nginx
    ports:
      - "8080:80"
    volumes:
      - static:/usr/share/nginx/html
      - media:/usr/share/nginx/html/media
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

2. **Переменные окружения для продакшена (.env):**

```env
# Django settings
DJANGO_ENVIRONMENT=production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain,your-ip-address
DJANGO_SECRET_KEY=your-secret-key-here
CSRF_TRUSTED_ORIGINS=your-domain-or-ip-address

# DB settings
USE_SQLITE=False
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432

# Gunicorn settings
GUNICORN_PORT=8080
```

### Запуск на сервере

```bash
# Копирование файлов на сервер
scp -i <path_to_ssh_key> /home/user/Dev/foodgram/docker-compose.production.yml user@server-ip:/home/user/foodgram/
scp -i <path_to_ssh_key> /home/user/Dev/foodgram/.env user@server-ip:/home/user/foodgram/

# Запуск на сервере
cd foodgram
sudo docker-compose -f docker-compose.production.yml up -d
```

## Структура проекта

```
foodgram/
├── backend/                    # Django приложение
│   ├── apps/                   # Django приложения
│   │   ├── api/                # API
│   │   ├── cart/               # Модель корзины
│   │   ├── recipes/            # Модели рецептов, тегов, ингредиентов
│   │   ├── users/              # Пользователи и подписки
│   │   └── core/                # Общие утилиты и базовые классы
│   ├── data/                   # Тестовые данные и фикстуры
│   ├── config/                  # Настройки Django проекта
│   ├── requirements/           # Зависимости Python
│   ├── logs/                   # Логи приложения
│   ├── media/                  # Загруженные файлы
│   ├── Dockerfile              # Docker образ для backend
│   ├── entrypoint.sh           # Скрипт запуска контейнера
│   ├── import_data.sh          # Скрипт импорта данных
│   ├── manage.py               # Django management команды
│   └── db.sqlite3             # SQLite база (для разработки)
├── frontend/                   # React приложение
├── nginx/                      # Конфигурация веб-сервера
│   ├── docs/                   # Документация API
│   ├── Dockerfile              # Docker образ для Nginx
│   └── nginx.conf              # Конфигурация Nginx
├── postman_collection/         # Коллекция для тестирования API
├── docker-compose.yml          # Локальная разработка
├── docker-compose.production.yml  # Продакшен конфигурация
├── pyproject.toml              # Конфигурация ruff
├── setup.cfg                   # Конфигурация flake8/isort
├── LICENSE                     # Лицензия проекта
└── README.md                   # Документация проекта
```

## Скрипты управления

### Команды Django Management

```bash
# Загрузка ингредиентов из CSV файла
python manage.py import_csv <model_cls> <path_to_data>
```


```bash
 # Автоматическое создания суперпользователя с данными:
 #   username = 'root'
 #   email = 'root@mail.com'
 #   password = 'root'
 #   first_name = 'root'
 #   last_name = 'rooot'
 python manage.py create_root
```

##  Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## Лицензия

Проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## Автор

GitHub: [@Khoetskiy](https://github.com/Khoetskiy)

## Поддержка

При возникновении вопросов или проблем:
- Создайте [Issue](https://github.com/Khoetskiy/foodgram/issues) в репозитории
- Свяжитесь с автором через GitHub

---
Если проект был полезен, поставьте звездочку!
