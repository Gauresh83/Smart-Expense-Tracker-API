# Smart Expense Tracker API

A robust, production-ready REST API for tracking personal and business expenses — built with **Django 5**, **Django REST Framework**, **PostgreSQL**, **Celery**, and **Redis**.

---

## Features

- **JWT Authentication** — short-lived access tokens (15 min) with rotating refresh tokens (7 days) and Redis blacklisting on logout
- **Expense Management** — full CRUD, bulk create (up to 100), receipt image uploads, recurring expense support
- **Category & Budget Tracking** — per-category budgets with configurable alert thresholds
- **Analytics** — period summaries, category breakdowns, month-over-month trends, top expenses
- **Async Tasks (Celery + Redis)** — budget alerts, monthly report emails, on-demand CSV exports
- **Email via SendGrid** — transactional emails with dynamic templates
- **Security** — `IsOwner` permission on all resources, rate limiting on auth endpoints, sensitive data log scrubbing
- **Docker Compose** — one-command local dev setup including PostgreSQL, Redis, Celery worker, Beat scheduler, and Flower

---

## Project Structure

```
expense_tracker/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── development.py   # Local dev overrides
│   │   └── production.py    # Prod: HTTPS, S3, Sentry
│   ├── celery.py            # Celery app + Beat schedule
│   └── urls.py              # Root URL config
├── apps/
│   ├── accounts/            # Custom User model, JWT auth, password reset
│   ├── expenses/            # Expense & Category models, ViewSets, filters
│   ├── budgets/             # Budget model, utilization status endpoint
│   ├── analytics/           # Read-only aggregation views
│   └── notifications/       # All Celery tasks (alerts, exports, reports)
├── common/
│   ├── permissions.py       # IsOwner, IsOwnerOrReadOnly
│   ├── pagination.py        # Cursor-based pagination
│   ├── exceptions.py        # Consistent error envelope
│   └── logging.py           # SensitiveDataFilter
├── tests/
│   ├── factories.py         # factory_boy fixtures
│   ├── unit/                # Model-level tests
│   └── integration/         # Full API endpoint tests
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── pytest.ini
└── requirements.txt
```

---

## Quick Start

### 1. Clone and configure

```bash
git clone <your-repo>
cd expense_tracker
cp .env.example .env
# Edit .env with your database, Redis, and SendGrid credentials
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Django API** on http://localhost:8000
- **Celery worker** (4 concurrent workers)
- **Celery Beat** (scheduled tasks)
- **Flower** (task monitor) on http://localhost:5555

### 3. Run locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Redis separately, then:
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# In separate terminals:
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

---

## API Endpoints

### Authentication — `/api/v1/auth/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `register/` | Create new account |
| POST | `login/` | Obtain access + refresh JWT |
| POST | `token/refresh/` | Rotate refresh token |
| POST | `logout/` | Blacklist refresh token |
| PUT | `password/change/` | Change password |
| POST | `password/reset/` | Request reset email |
| POST | `password/reset/confirm/` | Confirm reset |

### User — `/api/v1/users/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET / PATCH | `me/` | View or update profile |
| DELETE | `me/` | Soft-deactivate account |

### Expenses — `/api/v1/expenses/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List expenses — filterable by date, category, amount |
| POST | `/` | Create expense |
| GET | `/{id}/` | Retrieve expense |
| PATCH | `/{id}/` | Partial update |
| DELETE | `/{id}/` | Delete expense |
| POST | `/bulk/` | Bulk create (max 100) |
| POST | `/export/` | Async CSV/PDF export (returns `task_id`) |

**Query params:** `date_from`, `date_to`, `category`, `min_amount`, `max_amount`, `recurrence`, `currency`, `ordering`, `search`

### Categories — `/api/v1/categories/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET / POST | `/` | List or create categories |
| GET / PATCH / DELETE | `/{id}/` | Manage single category |

### Budgets — `/api/v1/budgets/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET / POST | `/` | List or create budgets |
| GET / PATCH / DELETE | `/{id}/` | Manage single budget |
| GET | `/{id}/status/` | Current spend vs. limit for active period |

### Analytics — `/api/v1/analytics/`

| Method | Endpoint | Query Params |
|--------|----------|--------------|
| GET | `summary/` | `period` (week/month/year) |
| GET | `by-category/` | `date_from`, `date_to` |
| GET | `trends/` | `months` (default 6) |
| GET | `top-expenses/` | `limit`, `period` |

---

## Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

Access tokens expire in **15 minutes**. Use `POST /api/v1/auth/token/refresh/` with your refresh token to obtain a new pair silently.

---

## Running Tests

```bash
pytest
# or with coverage report:
pytest --cov=apps --cov-report=html
```

---

## Celery Tasks

| Task | Trigger | Description |
|------|---------|-------------|
| `send_budget_alert` | On expense create | Fires when spend crosses `alert_threshold` % |
| `check_all_budget_utilizations` | Every hour (Beat) | Sweeps all budgets for all users |
| `generate_monthly_reports_for_all_users` | 1st of month, 08:00 UTC (Beat) | Sends monthly summary emails |
| `export_expenses_csv` | On-demand (POST /export/) | Generates CSV and emails download link |
| `send_password_reset_email` | On reset request | Sends password reset link |

Monitor task state at **http://localhost:5555** (Flower).

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DB_*` | PostgreSQL connection settings |
| `REDIS_URL` | Redis connection URL |
| `SENDGRID_API_KEY` | SendGrid API key |
| `AWS_*` | S3 credentials for receipt storage (production) |
| `FRONTEND_URL` | Base URL for password reset links |
| `SENTRY_DSN` | Sentry error tracking DSN (production) |

---

## Security

- Object-level `IsOwner` permission blocks horizontal privilege escalation
- Rate limiting: 5 req/min on auth endpoints, 60 req/min on write endpoints
- JWT refresh token blacklisting via Redis
- Receipt uploads: MIME + magic-byte validation, 5 MB limit, served via pre-signed S3 URLs
- `SensitiveDataFilter` strips passwords and tokens from all log output
- Production settings enforce HTTPS, HSTS (1 year), and `SECURE_CONTENT_TYPE_NOSNIFF`
