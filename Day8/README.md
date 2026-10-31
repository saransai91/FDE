# Day8 — Employee Performance Review

Built API-first: FastAPI (BFF) + PostgreSQL + React.

| Step | Deliverable | Status |
|------|-------------|--------|
| 1 | [Requirements (discovery Q&A)](docs/01-requirements.md) | Approved |
| 2 | [Technical design](docs/02-technical-design.md), [OpenAPI spec](docs/employee-performance-review-openapi.yaml), [schema.sql](backend/db/schema.sql), [seed.sql](backend/db/seed.sql) | Approved |
| 3 | Backend: API → Service → Repository → DB, Models, with tests | Built; awaiting Swagger review |
| 4 | Frontend: React Review Form and Review List, with tests | Not started |
| 5 | Optional: details, edit, delete, dashboard | Not started |
| 6 | Optional: simple login | Not started |

## Backend: run locally (PowerShell, from `Day8/backend`)

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env                 # then set your Postgres password in .env
.venv\Scripts\python db\init_db.py     # creates DB performance_review, applies schema + seed
.venv\Scripts\uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/api/docs

## Backend tests

```powershell
.venv\Scripts\python -m pytest -v
```

| Folder | Layer | Needs DB? |
|--------|-------|-----------|
| `tests/api/test_api_mocked.py` | API (services mocked) | No |
| `tests/api/test_api_e2e.py` | API → DB end-to-end | Yes |
| `tests/services/` | Service and validation rules (repositories mocked) | No |
| `tests/repositories/` | Repository queries | Yes |
| `tests/db/` | Schema constraints (raw SQL) | Yes |

DB tests use a separate database, `performance_review_test`. It is recreated on every run, and each test is rolled back. If Postgres is unreachable, those tests are skipped.
