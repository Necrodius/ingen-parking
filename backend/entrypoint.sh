#!/usr/bin/env sh
set -e  # Exit immediately if a command exits with a non-zero status

echo "Running Alembic migrations..."
alembic stamp base

echo "Seeding database..."
python seed.py

echo "Launching Gunicorn..."
exec gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --log-level info \
    --access-logfile - \
    --error-logfile  -
