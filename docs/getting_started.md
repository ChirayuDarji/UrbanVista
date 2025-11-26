# Getting Started

## Local (no Docker)

1. Create and activate a virtualenv
2. `pip install -r requirements.txt`
3. Create `.env` with:
   - `DJANGO_SECRET_KEY=dev-change-me`
   - `DEBUG=True`
   - `ALLOWED_HOSTS=127.0.0.1,localhost`
   - `REDIS_URL=` (optional)
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`

## Celery (optional locally)

- Run worker: `celery -A mysite worker -l info`
- Run beat: `celery -A mysite beat -l info`

## Tests

- `pytest` (uses `pytest.ini`)


