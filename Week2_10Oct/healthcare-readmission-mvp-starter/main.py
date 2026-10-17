from fastapi import FastAPI, HTTPException, Query
from models import InterventionUpdate
import service

app = FastAPI(
    title="Diabetes Readmission Intervention Queue",
    description="Learning prototype only; not for clinical decision-making.",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/encounters")
def list_encounters(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return service.list_encounters(limit=limit, offset=offset)

@app.get("/encounters/{encounter_id}")
def get_encounter(encounter_id: int):
    item = service.get_encounter(encounter_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return item

@app.get("/care-queue")
def care_queue(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return service.get_care_queue(limit=limit, offset=offset)

@app.get("/care-queue/high")
def high_risk_queue(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return service.get_high_risk_queue(limit=limit, offset=offset)

@app.patch("/interventions/{encounter_id}")
def update_intervention(encounter_id: int, payload: InterventionUpdate):
    try:
        return service.update_intervention(encounter_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.get("/operations/summary")
def operations_summary():
    return service.operations_summary()

@app.get("/operations/readmission-analysis")
def readmission_analysis():
    return service.readmission_analysis()

@app.get("/management/dashboard")
def management_dashboard():
    return service.management_dashboard()
