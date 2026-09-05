# Contributing

## Branch Strategy

```
main                    <- always demo-ready
 └── dev                <- integration branch, PR target for everyone
      ├── feature/frontend-<module>
      ├── feature/backend-<module>
      └── feature/database-<module>
```

Rules:
- Branch off `dev`, never off `main`.
- Open PRs into `dev`, not `main`.
- Merge `dev` -> `main` only at checkpoints (e.g. Tier 1 complete, final submission).
- Rebase/merge latest `dev` into your feature branch every 1-2 hours — with 3 people
  and a 24-hour clock, schema/API drift compounds fast otherwise.
- Delete feature branches after merging; don't keep long-lived personal branches.

Example branch names:
- `feature/frontend-purchase-flow`
- `feature/backend-accounting-engine`
- `feature/database-journal-schema`

## Ownership

| Developer | Owns |
|---|---|
| Frontend | `frontend/` (entire folder) |
| Backend | `backend/app/api/`, `backend/app/services/`, `backend/app/schemas/`, `backend/app/auth/` |
| Database | `database/` (migrations, seed, schema docs), `backend/app/models/`, Alembic configuration, `backend/app/core/database.py` |

**Important correction preserved from the architecture review:**
Pydantic schemas (`backend/app/schemas/`) belong to the **Backend**
developer, not Database — they are API contracts, not DB structure.

## Shared-Touch Files (handle with care)

These files are legitimately touched by more than one person. Keep
edits small and additive to avoid conflicts:

| File | Why it's shared | How to avoid conflicts |
|---|---|---|
| `backend/app/models/` | Database dev owns column definitions; Backend dev may need relationship helpers | Database dev commits first per entity; Backend dev only adds via follow-up PR, pings before editing columns |
| `backend/app/api/v1/__init__.py` | Every new route module needs one line here | Keep it to one import + one `include_router` line per module — never reorder or reformat existing lines in your PR |
| `frontend/src/App.jsx` / `frontend/src/routes/*.routes.jsx` | Routing grows as pages are added | Routes are split by domain (`auth`, `masters`, `transactions`, `budget`, `reports`, `portal`) — only touch the file for your domain |
| `.env.example` / `database/alembic.ini` | Config edited when new env vars are needed | Database dev's file — others request changes via PR comment, don't edit directly |
| `backend/app/services/accounting_engine.py` | Central, high-value file | Single-owner (Backend dev) — others file a request rather than editing directly |

## Development Workflow

1. **Hour 0-1** (all 3 together): confirm the API contract and DB
   schema in `docs/database-design.md` / `docs/api-documentation.md`
   before writing implementation code.
2. Database dev scaffolds `models/`, first Alembic migration, and
   `seed_data.py` first — push to `dev` within hour 1 so nobody is blocked.
3. Backend dev implements Auth -> Master CRUD -> Accounting Engine ->
   Purchase flow -> Sales flow -> Reports, in that order (see
   `docs/workflows.md` for the full priority tiers).
4. Frontend dev implements Layouts + Auth -> Master pages ->
   transaction pages -> Reports/Budget UI, integrating against real
   endpoints as soon as each one is live (don't wait for "everything"
   to be done before wiring up).
5. Short sync every 3-4 hours to re-check the API contract hasn't drifted.

## Commit Messages

Keep them short and prefixed by area, e.g.:
- `backend: implement vendor bill confirmation`
- `frontend: wire contact list to API`
- `database: add budget revision_of_id column`

## Pull Requests

- Target `dev`.
- One PR per module/feature — avoid bundling unrelated changes.
- Note in the PR description which MUST HAVE / SHOULD HAVE / NICE TO
  HAVE tier the change belongs to (see `docs/workflows.md`).
