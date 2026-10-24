from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import service
from models import (
    Encounter,
    HighCarePatient,
    InterventionUpdate,
    InterventionUpdateCreate,
    PatientSearch,
)

app = FastAPI(title="Diabetes Patient Management API")

# Allow the React app (Vite dev server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

service.init_db()


@app.get("/")
def root():
    return {"message": "Diabetes Patient Management API is running"}


# Declared before /encounters/{encounter_id} so "search" isn't parsed as an id
@app.get("/encounters/search", response_model=list[Encounter])
def search_patients(filters: Annotated[PatientSearch, Query()]):
    """Search by patient_id and/or min_risk_score and/or risk_level (all optional, ANDed)."""
    return service.search_patients(filters)


@app.get("/encounters/{encounter_id}", response_model=Encounter)
def get_encounter(encounter_id: int):
    encounter = service.get_encounter(encounter_id)
    if encounter is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@app.get("/patients/high-care", response_model=list[HighCarePatient])
def list_high_care_patients():
    """High-risk encounters with their latest intervention status."""
    return service.list_high_care_patients()


@app.get("/encounters/{encounter_id}/interventions", response_model=list[InterventionUpdate])
def get_intervention_history(encounter_id: int):
    try:
        return service.get_intervention_history(encounter_id)
    except service.EncounterNotFound:
        raise HTTPException(status_code=404, detail="Encounter not found")


@app.post(
    "/encounters/{encounter_id}/interventions",
    response_model=InterventionUpdate,
    status_code=201,
)
def update_intervention_status(encounter_id: int, data: InterventionUpdateCreate):
    try:
        return service.update_intervention_status(encounter_id, data)
    except service.EncounterNotFound:
        raise HTTPException(status_code=404, detail="Encounter not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
