#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

git pull origin main

docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo ""
if docker compose -f docker-compose.prod.yml exec web python manage.py migrate --check; then
    echo "Done. No new migrations."
else
    echo "Done. WARNING: there are unapplied migrations - run migrate manually:"
    echo "  docker compose -f docker-compose.prod.yml exec web python manage.py migrate"
fi
