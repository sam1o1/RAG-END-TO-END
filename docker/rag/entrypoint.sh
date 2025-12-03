#!/bin/bash
set -e
echo "Running database migrations..."
cd /app/models/db_schemas/rag
alembic upgrade head
echo "Database migrations completed."
cd /app
exec "$@"

