# Employee Performance Review System — Design (frozen)

Order of work: **freeze design → backend → frontend**. The contract below is the source of truth for integration.

- DB DDL: [../backend/db/schema.sql](../backend/db/schema.sql), seed: [../backend/db/seed.sql](../backend/db/seed.sql)
- API contract: [openapi.json](openapi.json) (exported from the running app; live at `/api/docs`)

## 1. Architecture

```
React (Vite, TS)  ──/api──▶  FastAPI
  pages/  Submit · My reviews · Detail        routers/        HTTP, params, status codes
  api/client.ts  fetch wrappers                  │
                                               services.py     business rules, average calc
                                                 │
                                               repositories.py all SQL (SQLAlchemy 2)
                                                 │
                                               PostgreSQL 18   employee_review (data on disk → survives restarts)
```

Routers call only services, and services call only repositories. Services raise `NotFoundError` (404), `ConflictError` (409), or `BusinessRuleError` (422). The database repeats every rule with constraints, so bad data is rejected even if someone bypasses the API.

## 2. Database (3 tables)

| Table | Kind | Key columns |
|-------|------|-------------|
| `employees` | master | `employee_id` VARCHAR PK (e.g. `EMP101`), name, department, designation, email (unique), status `Active/Inactive` |
| `review_periods` | master | `review_period_id` SERIAL PK, name (unique, e.g. `H1 2026`), `period_type` `Monthly/Quarterly/Half-Yearly/Annual`, start/end date, status `Open/Closed` |
| `performance_reviews` | transactional | `review_id` PK, `employee_id` FK, `review_period_id` FK, `quality_rating`, `delivery_rating`, `teamwork_rating`, `average_rating`, `comments`, `created_at` |

Data rules and where they are enforced:

| Rule | DB | API |
|------|----|-----|
| Ratings are 1–5 | `CHECK BETWEEN 1 AND 5` | Pydantic `ge=1, le=5` |
| Average = (quality + delivery + teamwork) ÷ 3 | stored `NUMERIC(3,2)` | `services.calculate_average` (round half-up, 2 dp) |
| One review per employee per period | `UNIQUE (employee_id, review_period_id)` | 409 Conflict |
| Comments mandatory | `NOT NULL` + non-blank `CHECK` | 422 |
| Employee must exist before review | FK `ON DELETE RESTRICT` | 422 |
| Only open periods accept reviews | — | 422 if `status = 'Closed'` (all seeded periods are Open for testing) |
| Only active employees are reviewed | — | 422 if `Inactive` |

Adding monthly or quarterly periods later only needs new rows in `review_periods`. No schema change is required.

## 3. API (base `/api`)

| Method | Path | Purpose | Responses |
|--------|------|---------|-----------|
| GET | `/employees` | All employees (dropdowns) | 200 `Employee[]` |
| GET | `/employees/{employee_id}` | One employee | 200, 404 |
| GET | `/review-periods` | Period master data (dropdown) | 200 `ReviewPeriod[]` |
| GET | `/reviews?employee_id=&review_period_id=&page=&page_size=` | List/search; both filters optional; `page_size` is 5 or 10 | 200 `ReviewPage`, 422 |
| GET | `/reviews/{review_id}` | Detail screen | 200 `Review`, 404 |
| POST | `/reviews` | Submit a review | 201 `{message, review}`, 409, 422 |

`ReviewPage` = `{ items: Review[], total, page, page_size, total_pages, average_rating }`. `average_rating` is the mean over **all** reviews that match the filters, not only the current page. For example, with `employee_id=EMP101` it is that employee's overall average.

POST body:
```json
{ "employee_id": "EMP102", "review_period_id": 3, "quality_rating": 4,
  "delivery_rating": 5, "teamwork_rating": 4, "comments": "Delivered all sprint stories on time." }
```

When the sample JSON arrives, import it into Swagger and diff its paths and fields against [openapi.json](openapi.json).

## 4. Screens

| Menu | Route | Screen |
|------|-------|--------|
| Submit reviews | `/submit` | Input form: employee dropdown (active only), period dropdown (open only), 3 ratings (1–5), live average, mandatory comments |
| My reviews | `/reviews` | Filters (period, single employee, 5/10 rows), summary (count + average), table, Previous/Next, **View** |
| (row → View) | `/reviews/:id` | Detail: employee, period, rating bars, average formula, comments, link to all of the employee's reviews |

The filters are kept in the URL, so going back from the detail screen restores them. Colors are tokens in `frontend/src/styles/theme.css`. Swap those tokens for the official color sheet.

## 5. Future (not built)

Edit/delete reviews (`PUT`/`DELETE /reviews/{id}`), login → SSO, an optional 4th screen (e.g. team dashboard).
