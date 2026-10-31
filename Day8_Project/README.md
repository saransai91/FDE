# Day8_Project — Employee Performance Review System

Managers submit frequent reviews (each sprint or review period) and search them by employee and period.
Stack: **FastAPI + SQLAlchemy + PostgreSQL** backend, **React 19 + Vite + TypeScript** frontend.

Design (tables, API, screens, rules): [docs/design.md](docs/design.md) · API contract: [docs/openapi.json](docs/openapi.json)

```
Day8_Project/
  docs/        design.md, openapi.json
  backend/     app/ (routers → services → repositories → models), db/ (schema, seed, init), tests/
  frontend/    src/ (pages, components, api client, styles), tests/
```

## Run

Prerequisite: PostgreSQL running locally (tested with 18).

**Backend** (from `backend/`):
```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env                     # set your Postgres password
.venv\Scripts\python db\init_db.py         # creates DB employee_review + seed (keeps data if it already exists)
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```
- Swagger: http://localhost:8000/api/docs
- `python db\init_db.py --reset` wipes the data and re-seeds it.

**Frontend** (from `frontend/`):
```powershell
npm install
npm run dev                                # http://localhost:5173 (proxies /api → :8000)
```
If the backend runs on another port: `$env:API_PROXY_TARGET="http://localhost:8001"; npm run dev`

## Tests

| Command | What |
|---------|------|
| `backend> .venv\Scripts\python -m pytest` | 75 tests: `tests/unit` (services and validation, no DB), `tests/api` (HTTP → Postgres end-to-end), `tests/db` (constraints, raw SQL) |
| `frontend> npm test` | 14 tests (Vitest + Testing Library): rating input, submit form, list/filter/pagination, detail |

DB tests run against `employee_review_test`. That database is rebuilt on every run, and each test is rolled back. If Postgres is down, those tests are skipped.

## Acceptance criteria

| Criterion | Where |
|-----------|-------|
| ✅ Submit a new review | "Submit reviews" screen → `POST /api/reviews` |
| ✅ Filter by employee and review period | "My reviews" filters → `GET /api/reviews?employee_id=&review_period_id=` |
| ✅ Average rating for an employee's reviews | Summary card on "My reviews" (`average_rating` across all matching reviews) |
| ✅ Rating values shown clearly | Quality / Delivery / Teamwork / Average columns; rating bars on the detail screen |
| ✅ Data persists after restart | Stored in Postgres; `init_db.py` never wipes data without `--reset` (verified by restarting the API) |
| ✅ Swagger matches the contract | `/api/docs`; exported to `docs/openapi.json` |
| ✅ Detail screen and filter-by-employee | "View" → `/reviews/:id`; "See all reviews for …" link |
| ➖ Edit/delete | Future |
