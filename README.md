# Urban Furniture Accounting System

A 24-hour hackathon project: an accounting system for Urban Furniture
covering master data (Contacts, Products, Chart of Accounts, Journals,
Analytic Accounts, Budgets), the Purchase and Sales transaction
flows, a centralized double-entry Accounting Engine, and automated
financial reporting (Balance Sheet, Profit & Loss, Budget Report).

This repository is a clean starting scaffold — models, schemas,
routes, and services exist as structured placeholders with TODOs.
Business logic is implemented by the team following the priority
order in `docs/workflows.md`.

## 1. Project Purpose

Built from the official Problem Statement + Excalidraw MVP mockups.
See `docs/architecture.md` for the full requirement audit and
`docs/database-design.md` for the entity model.

Core principle: every transaction that affects money (Vendor Bill,
Customer Invoice, Payment) flows through **one** centralized
Accounting Engine (`backend/app/services/accounting_engine.py`) that
creates balanced Journal Entries. No other module computes debits/
credits independently.

## 2. Architecture

```
Business Transaction
        |
        v
Accounting Service (accounting_engine.py)
        |
        v
Journal Entry
        |
        v
Journal Entry Lines   <-- SUM(debit) == SUM(credit), enforced
        |
        v
Ledger
        |
        v
Financial Reports
```

Modular monolith, monorepo, REST API. No microservices, no Docker/
Kubernetes/Redis/message queues — kept intentionally simple for a
24-hour build.

## 3. Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React + Vite + React Router |
| Backend | Python + FastAPI + SQLAlchemy + Pydantic |
| Database | PostgreSQL + Alembic (migrations) |
| API | REST |

## 4. Folder Structure

```
urban-furniture-accounting/
├── frontend/     # React + Vite app
├── backend/      # FastAPI app (api / models / schemas / services / auth / core)
├── database/     # Alembic migrations, seed data, ER diagram
├── docs/         # Architecture, DB design, API docs, workflows, setup
├── .gitignore
├── .env.example
├── README.md
└── CONTRIBUTING.md
```

See `docs/architecture.md` for what each folder is responsible for
and who owns it.

## 5. Local Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+

### 5.1 Clone & environment

```bash
git clone <repo-url>
cd urban-furniture-accounting
cp .env.example .env
# edit .env with your local DATABASE_URL / SECRET_KEY
```

### 5.2 PostgreSQL setup

```bash
# create the database referenced in DATABASE_URL
createdb urban_furniture
```

### 5.3 Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# run migrations (from database/, see below)
cd ../database
alembic upgrade head

# seed demo master data (optional, safe/idempotent)
python seed/seed_data.py

# run the API
cd ../backend
uvicorn app.main:app --reload
# API available at http://localhost:8000, docs at /docs
```

### 5.4 Frontend setup

```bash
cd frontend
cp .env.example .env   # sets VITE_API_BASE_URL
npm install
npm run dev
# app available at http://localhost:5173
```

### 5.5 Migration commands (run from `database/`)

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
alembic downgrade -1   # roll back one revision if needed
```

## 6. How the Team Should Work

We are 3 developers: **Frontend**, **Backend**, **Database**.

| Owner | Primary folders |
|---|---|
| Frontend | `frontend/` |
| Backend | `backend/app/api/`, `backend/app/services/`, `backend/app/schemas/`, `backend/app/auth/` |
| Database | `database/`, `backend/app/models/`, Alembic config |

See `CONTRIBUTING.md` for the branch strategy and how to avoid merge
conflicts on shared files (router registration, `App.jsx`, model
files).

## 7. Key Documents

- `docs/architecture.md` — full requirement audit + accounting architecture
- `docs/database-design.md` — entity list, fields, relationships
- `docs/api-documentation.md` — API module list + endpoints
- `docs/workflows.md` — end-to-end business workflows + demo flow
- `docs/setup-instructions.md` — expanded setup/troubleshooting notes
