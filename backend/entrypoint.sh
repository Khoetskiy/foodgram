#!/bin/bash

set -e

echo "=== Starting Django Application ==="

echo "Waiting for services to start..."
sleep 5

echo "Creating database migrations..."
python manage.py makemigrations --no-input

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:${GUNICORN_PORT:-8000}
