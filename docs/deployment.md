# Deployment

- Use Docker and docker-compose included.
- Services: web (Gunicorn), worker (Celery), beat (Celery Beat), Redis, Postgres.

## Quick start

1. Create `.env` with your secrets (DJANGO_SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, REDIS_URL, DB config if not using compose defaults)
2. Build: `docker compose build`
3. Run: `docker compose up -d`
4. Exec web: `docker compose exec web python manage.py migrate && python manage.py collectstatic --noinput`
5. Create admin: `docker compose exec web python manage.py createsuperuser`

## Environment

- `REDIS_URL=redis://redis:6379/1`
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` default to `REDIS_URL`
- `DJANGO_SETTINGS_MODULE=mysite.settings` (split settings optional)


