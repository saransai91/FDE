# Employee Performance Review — Technical Design

Status: **APPROVED (2026-10-25)**

Contract files:
- API: [employee-performance-review-openapi.yaml](employee-performance-review-openapi.yaml)
- DB: [../backend/db/schema.sql](../backend/db/schema.sql) and [../backend/db/seed.sql](../backend/db/seed.sql)

## 1. Architecture

```
React (Vite, TS) ──HTTP/JSON──▶ FastAPI (BFF)
                                  api/          routers: HTTP, status codes, query params
                                    │
                                  services/     business rules (BR-1..BR-7), average calc
                                    │
                                  repositories/ all DB queries (SQLAlchemy)
                                    │
                                  db/           engine, session, schema.sql, seed.sql
                                    │
                                PostgreSQL 18 (performance_review)

                                  models/       SQLAlchemy ORM tables
                                  schemas/      Pydantic request/response DTOs
```

Rules for the layers:
- Routers only call services. Services only call repositories. Repositories are the only code that touches the session.
- Services raise domain errors (`NotFoundError`, `ConflictError`, `BusinessRuleError`). The API layer maps them to 404 / 409 / 422.
- The DB also enforces integrity (FKs, CHECKs, UNIQUE), so it is protected even if the API is bypassed.

## 2. Tech stack

| Layer | Choice |
|-------|--------|
| API | FastAPI, Uvicorn, Pydantic v2 |
| Data | SQLAlchemy 2.0, psycopg 3 |
| DB | PostgreSQL 18 (already running locally) |
| Backend tests | pytest, FastAPI TestClient, separate DB `performance_review_test` |
| Frontend | React 19, Vite, TypeScript, react-router |
| Frontend tests | Vitest, React Testing Library, jsdom |

## 3. Folder layout

```
Day8/
  docs/                      requirements, design, OpenAPI
  backend/
    app/
      main.py                app factory, CORS, router registration
      config.py              settings from .env
      api/                   employees.py, review_periods.py, reviews.py, errors.py
      services/              employee_service.py, review_period_service.py, review_service.py
      repositories/          employee_repository.py, review_period_repository.py, review_repository.py
      models/                employee.py, review_period.py, performance_review.py
      schemas/               employee.py, review_period.py, review.py
      db/                    session.py
    db/                      schema.sql, seed.sql, init_db.py
    tests/
      api/  services/  repositories/  db/
    requirements.txt  .env.example  pytest.ini
  frontend/
    src/
      api/                   client.ts (fetch wrappers)
      pages/                 ReviewFormPage.tsx, ReviewListPage.tsx
      components/            StarRating.tsx, Sidebar.tsx, Pagination.tsx
      types.ts
      __tests__/
```

## 4. Database design

Three tables. Changes from the screenshot, kept for integrity:

| Change | Reason |
|--------|--------|
| `employees.status` gets `CHECK (status IN ('Active','Inactive'))` | Only valid values can be stored. |
| `review_periods.status` gets `CHECK (status IN ('Open','Closed'))` and `CHECK (end_date >= start_date)` | BR-4, BR-7. |
| `review_periods.name` is `UNIQUE` | Avoids two "H1 2026" rows. |
| `employees.email` is `UNIQUE` | Natural key. |
| Rating columns get `CHECK (x BETWEEN 1 AND 5)` | BR-1. |
| `average_rating` gets `CHECK (BETWEEN 1 AND 5)` | Sanity check. |
| `comments` is `NOT NULL` with a non-blank CHECK | BR-6 (Q9). |
| `UNIQUE (employee_id, period_id)` on reviews | BR-3. |
| FKs use `ON DELETE RESTRICT` | Master data that has reviews cannot be deleted. |
| Indexes on `performance_reviews(period_id)` and `(employee_id)` | Fast list filters. |

The full DDL is in `backend/db/schema.sql`.

## 5. API design

Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description | Phase |
|--------|----------|-------------|-------|
| GET | /employees | List employees (`?status=Active` optional) | 1 |
| GET | /review-periods | List periods (`?status=Open` optional) | 1 |
| GET | /reviews | List reviews (`period_id`, `employee_id`, `page`, `page_size`) with `X-Total-Count` header | 1 |
| POST | /reviews | Submit a review → 201 | 1 |
| GET | /reviews/{id} | Review details | 2 (optional) |
| PUT | /reviews/{id} | Edit a review | 2 (optional) |
| DELETE | /reviews/{id} | Delete a review → 204 | 2 (optional) |
| GET | /reviews/summary/departments | Average rating by department | 2 (optional) |
| POST | /auth/login | Simple login → JWT | last (optional) |

Error codes:

| Code | When |
|------|------|
| 404 | The review id does not exist. |
| 409 | A review for this employee and period already exists. |
| 422 | Pydantic validation error, unknown employee or period, closed period, or inactive employee. |

## 6. Testing strategy

| Layer | What is tested | How |
|-------|----------------|-----|
| DB | Constraints reject bad data: rating 0 or 6, duplicate review, bad FK, `end_date < start_date`, blank comment | Raw SQL against the test DB |
| Repository | Create, list with filters and pagination, count, get by id | Real test DB, rolled back after each test |
| Service | Average calculation and rounding, closed period, inactive employee, duplicate, not found | Repositories mocked |
| API | Status codes, validation (422), response shape, `X-Total-Count` header | TestClient with services mocked, plus a few end-to-end tests on the test DB |
| UI | Star rating input, form validation and submit, list rendering, filters, pagination | Vitest + RTL with `fetch` mocked |

## 7. Delivery plan (each step is approved before the next starts)

1. ✅ Requirements and design (this document, OpenAPI, SQL) → **approval**
2. Backend: DB schema, seed, models, repositories, services, API, and tests → you review the Swagger docs
3. Frontend: Review Form and Review List, with tests
4. Optional features, one at a time, each with its own design and approval
5. Optional: simple login
