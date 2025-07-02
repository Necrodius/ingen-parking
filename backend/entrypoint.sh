#!/usr/bin/env sh
set -e  # Exit immediately if a command exits with a non-zero status

# Ommit on dev
echo "Running Alembic migrations..."
alembic stamp base

#Ommit on dev
echo "Seeding database..."
python seed.py

echo "Launching Gunicorn..."
exec gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --log-level info \
    --access-logfile - \
    --error-logfile  -
