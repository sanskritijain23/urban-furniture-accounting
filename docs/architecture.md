# Architecture

## Overview

Urban Furniture Accounting System — a modular monolith monorepo built
for a 24-hour hackathon. React+Vite frontend, FastAPI backend,
PostgreSQL database, REST API, centralized accounting engine.

No microservices, no Docker/Kubernetes, no Redis, no message queues —
deliberately excluded to optimize for speed and demoability within
the time limit.

## Centralized Accounting Architecture (non-negotiable)

```
Business Transaction (Vendor Bill / Customer Invoice / Payment / Manual Entry)
        |
        v
Accounting Service   (backend/app/services/accounting_engine.py)
        |
        v
Journal Entry
        |
        v
Journal Entry Lines     <-- SUM(debit) == SUM(credit), enforced here
        |
        v
Ledger   (backend/app/services/ledger_service.py — read-side aggregation)
        |
        v
Financial Reports  (Balance Sheet / P&L / Budget Report)
```

**Rule:** `accounting_engine.py` is the ONLY module permitted to
create or post `JournalEntry` / `JournalEntryLine` rows. Purchase,
sales, payment, and report services call into it — they never
compute debit/credit totals themselves.

### Which transactions create accounting entries

| Transaction | Creates Journal Entry? | Debit | Credit |
|---|---|---|---|
| Purchase Order confirm | **No** | — | — |
| Sales Order confirm | **No** | — | — |
| Vendor Bill confirm | **Yes** | Purchase Expense | Creditors (vendor) |
| Customer Invoice confirm | **Yes** | Debtors (customer) | Sales Income |
| Vendor Bill Payment | **Yes** (separate from Bill's entry) | Creditors | Bank/Cash |
| Customer Invoice Payment | **Yes** (separate from Invoice's entry) | Bank/Cash | Debtors |
| Manual Journal Entry | **Yes**, on explicit Post | user-selected | user-selected |

Every Payment always creates its own, separate Journal Entry from the
one created when the underlying Bill/Invoice was confirmed — they are
never merged into a single entry.

## Layered Backend Architecture

```
API routes (thin, no business logic)
        |
        v
Services / business logic (purchase_service, sales_service, payment_service, budget_service)
        |
        v
Accounting Service (accounting_engine.py)
        |
        v
Database (SQLAlchemy models)
```

## Requirement Audit Summary

The following were corrected/added after auditing the official
Problem Statement + MVP screenshots against an earlier draft
architecture (kept here for team reference — do not re-introduce
these gaps):

- Manual Journal Entry screen is a MUST HAVE, separate from
  auto-generated entries.
- Debit != Credit is a BLOCKING validation error on Post.
- Analytic Account is assigned per LINE ITEM on PO/SO/Bill/Invoice,
  not on the document header.
- Budget lifecycle is Draft -> Confirmed -> Revised -> Cancelled;
  revising creates a NEW linked record rather than mutating the
  original.
- Budget achieved amount / achieved % / amount-to-achieve are
  COMPUTED fields, never stored columns.
- Exceeding a budget is a NON-BLOCKING warning, not a hard error.
- Chart of Accounts `type` uses the 8-value enum (Asset, Liability,
  Bank, Cash, Capital, Income, Expenses, Other Expenses) — not a
  generic 5-value enum.
- Contact/Product/Analytic Account support both List and Kanban views.
- Contact Portal is strictly read + pay — no create/edit access.
- Three separate user-creation paths exist: admin "Create User" form,
  public signup (always creates an accountant), and auto-created
  contact logins from Contact Master.
- Bill/Invoice have both a system-generated number (`bill_no` /
  `invoice_no`) AND a separate free-text `reference` field.
- No stock/inventory valuation module — not supported by any MVP screen.

## Ownership

| Owner | Folders |
|---|---|
| Frontend Developer | `frontend/` |
| Backend Developer | `backend/app/api/`, `backend/app/services/`, `backend/app/schemas/`, `backend/app/auth/` |
| Database Developer | `database/`, `backend/app/models/`, Alembic config, `backend/app/core/database.py` |

See `CONTRIBUTING.md` for the full branch strategy and shared-file
conflict mitigation.
