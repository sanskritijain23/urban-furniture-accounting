# Setup Instructions (Expanded)

See the root `README.md` for the quick-start version. This document
covers extra detail and troubleshooting.

## 1. Environment Variables

Copy `.env.example` to `.env` at the repo root and fill in real local
values. Never commit `.env`.

| Variable | Used by | Notes |
|---|---|---|
| `DATABASE_URL` | backend, database/seed, Alembic | e.g. `postgresql://postgres:postgres@localhost:5432/urban_furniture` |
| `SECRET_KEY` | backend auth (JWT signing) | generate a random string, e.g. `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend auth | defaults to 60 |
| `APP_NAME` | backend | cosmetic, shown in FastAPI docs title |
| `ENV` | backend | `development` / `production` |

The frontend has its own `.env` (copied from `frontend/.env.example`)
with `VITE_API_BASE_URL` pointing at the backend.

## 2. PostgreSQL

Install PostgreSQL 14+ locally, or use a container/managed instance —
just point `DATABASE_URL` at it. Create the database referenced in
the URL before running migrations:

```bash
createdb urban_furniture
```

## 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Common issues:
- **ModuleNotFoundError: app** — run `uvicorn` from inside `backend/`,
  not the repo root.
- **psycopg2 build errors** — `requirements.txt` uses
  `psycopg2-binary` specifically to avoid needing system build tools;
  if issues persist, ensure you're on a supported Python version (3.11+).

## 4. Database / Alembic

Alembic is configured to run from the `database/` folder and imports
the backend's models via `app.models` (see `database/migrations/env.py`).

```bash
cd database
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

If `alembic` can't find the `app` package, check that
`database/migrations/env.py`'s `sys.path.insert(...)` line correctly
resolves to `../../backend` relative to your working directory.

## 5. Seed Data

```bash
cd database
python seed/seed_data.py
```

This is idempotent (checks for existing rows before inserting) and
only creates master data (Chart of Accounts, Journals, demo Contacts/
Products) — no fake completed transactions.

## 6. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

If the frontend can't reach the API, check `VITE_API_BASE_URL` in
`frontend/.env` matches where `uvicorn` is actually running (default
`http://localhost:8000/api/v1`).

## 7. Running Tests

```bash
cd backend
pytest
```

Test files currently contain placeholder assertions
(`test_placeholder`) — replace with real tests as each service's
business logic is implemented, starting with
`tests/test_accounting_engine.py` (the debit=credit invariant is the
highest-priority thing to test in this codebase).

## 8. Verifying the Scaffold Boots

Even before implementing business logic, you should be able to:

```bash
cd backend && uvicorn app.main:app --reload
# visit http://localhost:8000/health -> {"status": "ok", ...}
# visit http://localhost:8000/docs -> Swagger UI listing all routes
```

```bash
cd frontend && npm run dev
# visit http://localhost:5173 -> blank routed pages with "TODO" placeholders
```

Both should start without import errors — every route currently
raises `NotImplementedError` only when *called*, not at import time.
