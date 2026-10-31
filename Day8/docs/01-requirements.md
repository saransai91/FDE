# Employee Performance Review — Requirements

Status: **APPROVED (2026-10-25)**

## 1. Goal

Managers record a performance review for an employee for a review period
(for example H1 2026). They rate three criteria from 1 to 5, write comments,
and can list and search the reviews that were submitted.

## 2. Discovery questions and proposed answers

Answers marked **(assumed)** are my proposals. Please confirm or correct them.

| # | Question | Answer |
|---|----------|--------|
| Q1 | Who uses the app? | Managers / HR. There is one user role for now. **(assumed)** |
| Q2 | Which criteria are rated? | Quality of Work, Delivery & Ownership, Teamwork & Collaboration. |
| Q3 | What is the rating scale? | Whole numbers from 1 to 5 (star widget). Half stars are not allowed. |
| Q4 | How is the average calculated? | `(quality + delivery + teamwork) / 3`, rounded to 2 decimals and stored as `DECIMAL(3,2)`. The UI shows 1 decimal (4.33 → "4.3"). |
| Q5 | Who calculates the average? | The server (service layer). The client never sends it. |
| Q6 | Can an employee get two reviews in one period? | No. One review per employee per period, enforced by a DB unique constraint. A duplicate returns **409 Conflict**. |
| Q7 | Can a review be submitted for a Closed period? | No. The API returns **422** with a clear message. |
| Q8 | Can an Inactive employee be reviewed? | No. The API returns **422**. **(assumed)** |
| Q9 | Are comments mandatory? | Yes. Business rule 9 says "Comments are mandatory", which wins over the `NULL` shown in the draft table. The DB column is `NOT NULL`, and the API requires 1–2000 non-blank characters. **(assumed: please confirm)** |
| Q10 | What does the "Status" column on the list screen mean? | Every saved review is "Completed". There is no draft state, so there is no status column. The UI shows a fixed "Completed" badge. **(assumed)** |
| Q11 | How does the list filter? | Optional `period_id` and `employee_id`, combined with AND. "All Periods" / "All Employees" means no filter. |
| Q12 | Is the list paginated? | Yes. `page` (default 1) and `page_size` (default 5, max 100). The body stays a plain JSON array, matching the sample. The total is returned in the `X-Total-Count` header so the UI can show "Showing 1 to 5 of 12". **(assumed)** |
| Q13 | How is the list sorted? | Newest first (`created_at DESC`, then `id DESC`). **(assumed)** |
| Q14 | Are employees and periods managed in the app? | No. They are master data loaded by seed scripts. The API only reads them. |
| Q15 | Which periods show in the review form? | Only `Open` periods. The list screen filter shows all periods. |
| Q16 | Which employees show in the review form? | Only `Active` employees. |
| Q17 | Authentication? | Optional, built last. It is a simple username/password login that returns a JWT. SSO comes later. |
| Q18 | Where does it run? | Locally. API at `http://localhost:8000/api`, React at `http://localhost:5173`, PostgreSQL 18 at `localhost:5432`. |

## 3. Functional requirements

### Mandatory (phase 1)

| ID | Requirement |
|----|-------------|
| FR-1 | Submit a new performance review: employee, period, 3 ratings, comments. |
| FR-2 | Validate ratings (integer 1–5) and required fields, in both the UI and the API. |
| FR-3 | Calculate and store the average rating. |
| FR-4 | List reviews with optional period and employee filters, with pagination. |
| FR-5 | Show the average rating on the list. |
| FR-6 | Store data in PostgreSQL with referential integrity. |
| FR-7 | Provide read endpoints for employees and review periods (dropdowns). |
| FR-8 | Publish the OpenAPI spec and Swagger UI. |

### Optional (phase 2, if time permits, each one approved separately)

| ID | Requirement |
|----|-------------|
| FR-9 | Review details screen (`GET /reviews/{id}`). |
| FR-10 | Edit an existing review (`PUT /reviews/{id}`). |
| FR-11 | Delete a review (`DELETE /reviews/{id}`). |
| FR-12 | Summary dashboard: average rating by department. |
| FR-13 | Simple login (JWT). This one is built last. |

## 4. Business rules

| ID | Rule |
|----|------|
| BR-1 | Each rating is an integer between 1 and 5. |
| BR-2 | Average = (quality + delivery + teamwork) / 3, rounded to 2 decimals. |
| BR-3 | One review per employee per review period. |
| BR-4 | Only `Open` periods accept new reviews. |
| BR-5 | Only `Active` employees can be reviewed. |
| BR-6 | Comments are mandatory (max 2000 characters). |
| BR-7 | Review periods are half-yearly or annual, and `end_date` must be on or after `start_date`. |

## 5. Non-functional requirements

- Layered backend: **API → Service → Repository → DB**, with **Models** (ORM) and **Schemas** (Pydantic) kept separate.
- Unit tests at every layer: API, service, repository/DB, and UI.
- Seed data: 25 employees, 6 review periods, about 15 sample reviews.
- Configuration through a `.env` file (DB URL). No secrets in code.
- Error format: `{"detail": "<message>"}`, the FastAPI standard.
