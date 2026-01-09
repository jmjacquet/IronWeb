#!/bin/bash
set -e

echo "Starting IronWeb application..."

# Wait for database to be ready (if DB_HOST is set)
if [ -n "$DB_HOST" ]; then
    echo "Waiting for database at $DB_HOST:$DB_PORT..."
    while ! nc -z ${DB_HOST} ${DB_PORT:-3306}; do
        sleep 0.5
    done
    echo "Database is ready!"
fi

# Collect static files if needed
if [ "$COLLECT_STATIC" = "true" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput || true
fi



# Execute the main command
exec "$@"