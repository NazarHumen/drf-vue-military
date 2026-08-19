#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

git pull origin main

echo "Building web image..."
docker compose -f docker-compose.prod.yml build web

echo "Starting containers..."
docker compose -f docker-compose.prod.yml up -d

echo "Collecting static files..."
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo ""
if docker compose -f docker-compose.prod.yml exec web python manage.py migrate --check; then
    echo "Done. No new migrations."
else
    echo "Done. WARNING: there are unapplied migrations - run migrate manually:"
    echo "  docker compose -f docker-compose.prod.yml exec web python manage.py migrate"
fi
