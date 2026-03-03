#!/usr/bin/env bash

set -e

cd /app/fastapi-application
echo "Run apply migrations"
alembic upgrade head
echo "Migrations applied"

exec "$@"