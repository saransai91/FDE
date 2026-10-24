from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import service
from models import Encounter, EncounterCreate, PatientSearch

app = FastAPI(title="Diabetes Encounter API")

# Allow the React app (Vite dev server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

service.init_db()


@app.get("/")
def root():
    return {"message": "Encounter API is running"}


# Declared before /encounters/{encounter_id} so "search" isn't parsed as an id
@app.get("/encounters/search", response_model=list[Encounter])
def search_patients(filters: Annotated[PatientSearch, Query()]):
    """Search by patient_id and/or min_risk_score and/or risk_level (all optional, ANDed)."""
    return service.search_patients(filters)


@app.get("/encounters", response_model=list[Encounter])
def list_encounters():
    return service.list_encounters()


@app.get("/encounters/{encounter_id}", response_model=Encounter)
def get_encounter(encounter_id: int):
    encounter = service.get_encounter(encounter_id)
    if encounter is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@app.post("/encounters", response_model=Encounter, status_code=201)
def create_encounter(data: EncounterCreate):
    try:
        return service.create_encounter(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/encounters/{encounter_id}", status_code=204)
def delete_encounter(encounter_id: int):
    if not service.delete_encounter(encounter_id):
        raise HTTPException(status_code=404, detail="Encounter not found")
