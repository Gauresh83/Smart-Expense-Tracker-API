# Windows Setup Guide

## The psycopg2 problem

`psycopg2-binary` on Windows sometimes tries to compile from source instead of
using the pre-built wheel, which fails with *"pg_config executable not found"*.

## Fix — use the `--only-binary` flag

Run **one** of these instead of the plain `pip install -r requirements.txt`:

```powershell
# Option A — recommended, no PostgreSQL install needed on Windows
pip install -r requirements-windows.txt

# Option B — force pre-built wheel inline
pip install -r requirements.txt --only-binary=psycopg2-binary
```

## Full Windows quick-start

```powershell
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies (Windows-safe)
pip install -r requirements-windows.txt

# 3. Copy and edit environment config
copy .env.example .env
# Open .env in any editor and fill in DB_*, REDIS_URL, etc.

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser (optional)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

## Running Celery on Windows

Celery's default multiprocessing pool doesn't work on Windows. Use the
`solo` pool (single-threaded, fine for development):

```powershell
# Worker
celery -A config worker --loglevel=info --pool=solo

# Beat scheduler (separate terminal)
celery -A config beat --loglevel=info
```

## PostgreSQL on Windows

If you don't have PostgreSQL installed locally, the easiest options are:

1. **Docker Desktop** (recommended) — run `docker-compose up db redis` to start
   just the database and Redis, then run Django natively:
   ```powershell
   docker-compose up db redis -d
   python manage.py runserver
   ```

2. **PostgreSQL installer** — https://www.postgresql.org/download/windows/
   After installing, make sure `pg_config` is on your PATH if you ever need
   to compile psycopg2 from source.

3. **SQLite for quick prototyping** — add this to `.env`:
   ```
   USE_SQLITE=true
   ```
   Then add to `config/settings/development.py`:
   ```python
   import os
   if os.environ.get("USE_SQLITE"):
       DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
                                "NAME": BASE_DIR / "db.sqlite3"}}
   ```

## Running tests on Windows

```powershell
pytest tests/unit/          # model tests only (no DB connection needed beyond SQLite)
pytest tests/integration/   # full API tests (requires running PostgreSQL)
```
