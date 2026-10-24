# Day6 HW — Diabetes Patient Management

Search patients, list high care patients, and track intervention status.

Runs on its own ports so it doesn't clash with the Day6 app (8000 / 5173):
API on **8001**, UI on **5174**.

## Run

```bash
# 1. API  (Swagger: http://127.0.0.1:8001/docs)
cd backend
python -m uvicorn main:app --reload --port 8001

# 2. UI   (http://localhost:5174)
cd frontend
npm install
npm run dev
```

The SQLite database (`backend/encounters.db`) is created and seeded on first start.
Delete it to reset to the sample data.

## API

| Method | Path | Purpose |
|---|---|---|
| GET  | `/encounters/search?patient_id=&min_risk_score=&risk_level=` | (a) Search — all filters optional, ANDed |
| GET  | `/encounters/{id}` | One encounter |
| GET  | `/patients/high-care` | (b) High risk encounters + latest intervention status |
| GET  | `/encounters/{id}/interventions` | (c) Status history, newest first |
| POST | `/encounters/{id}/interventions` | (c) Add a status update `{status, assigned_to, notes}` |

Statuses: `Not Started`, `In Progress`, `Completed`, `Cancelled`.
`Assigned To` is required for `In Progress` and `Completed`.
Updates are appended (history is kept), so the "current" status is the latest update.

## Code layout

- `backend/main.py` — FastAPI routes
- `backend/service.py` — business rules (validation, not-found)
- `backend/repository.py` — all SQL, table creation, seed data
- `backend/models.py` — Pydantic models
- `frontend/src/api.ts` — typed fetch functions for every endpoint
- `frontend/src/PatientSearch.tsx` — (a) search screen
- `frontend/src/HighCarePatients.tsx` — (b) high care list
- `frontend/src/StatusTracking.tsx` — (c) status tracking screen (opened by clicking an Encounter Id)
