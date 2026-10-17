# Diabetes Readmission Intervention Queue

Learning prototype for the Testleaf Week 2 Forward Deployed Engineer mini project.

**Not clinically validated. Do not use for real patient-care decisions.**

## Business problem
Help a hospital care-management team review historical diabetes encounters in a prioritized queue and track follow-up interventions.

## Users
- Care-management team: prioritize and track cases.
- Hospital operations: monitor queue volume and backlog.
- Clinical leadership: inspect explainable scoring rationale.
- Finance/transformation: review historical outcome signals.

## Dataset
Place the course-provided encounter-data file `diabetic_data.csv` at `data/diabetic_data.csv`.
It must contain one row per encounter and columns including `encounter_id`,
`patient_nbr`, and `readmitted`. A field-description sheet (for example, with
`Field;Purpose` as its header) is not the dataset and cannot be loaded.
This prototype uses the selected encounter, utilization, length-of-stay, medication, discharge, admission and readmission fields.

## Risk rule
- `number_inpatient >= 3`: +3
- `number_emergency >= 2`: +2
- `number_outpatient >= 3`: +1
- `time_in_hospital >= 7`: +1
- `num_medications >= 20`: +1
- 0–2 LOW; 3–4 MEDIUM; 5+ HIGH

The `readmitted` outcome is not used to calculate risk. It is used only in retrospective evaluation; `<30` is treated as readmission within 30 days for the common UCI dataset. Confirm this encoding in your supplied CSV.

## Setup on Windows
1. Install Python and PostgreSQL.
2. Create database `healthcare_readmission`.
3. In PowerShell, from this folder:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```
4. Edit `.env` and replace `YOUR_PASSWORD` with your PostgreSQL password.
5. Run `schema.sql` in pgAdmin's Query Tool while connected to `healthcare_readmission`.
6. Place the CSV at `data/diabetic_data.csv`.
7. Run:
   ```powershell
   python data_loader.py
   uvicorn main:app --reload
   ```
8. Open http://127.0.0.1:8000/docs.

## API endpoints
- `GET /encounters`
- `GET /encounters/{encounter_id}`
- `GET /care-queue`
- `GET /care-queue/high`
- `PATCH /interventions/{encounter_id}`
- `GET /operations/summary`
- `GET /operations/readmission-analysis`
- `GET /management/dashboard`

## Assumptions and limitations
- This is a learning prototype, not a clinical score.
- Missing numeric values are set to zero by the starter loader; review and justify this assumption before final submission.
- Re-running the loader upserts encounter records.
- `CLOSED` is counted as a completed intervention.
- Readmission rates are retrospective associations, not proof of preventability or causation.
- Intervention status transitions are validated against the allowed status values, but strict sequential transitions are not enforced.

## FDE reflection
Complete these based on your actual results:
1. What business problem did you solve?
2. Who is the primary user?
3. What decision does your application improve?
4. What did the dataset prove? Use measured results, not assumptions.
5. What assumptions did you make?
6. What must the hospital validate before this could become a real product?
7. Would you use rules, traditional ML, an LLM, or another approach next—and why?

## Demo plan (3–5 minutes)
Show CSV ingestion, PostgreSQL record counts, Swagger endpoints, the care queue, a persisted intervention update, operational metrics, and historical readmission analysis.
