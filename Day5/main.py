from fastapi import FastAPI, HTTPException

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
encounters = [
    {
        "encounter_id": 101,
        "patient_id": 1001,
        "risk_score": 25,
        "risk_level": "Low"
    },
    {
        "encounter_id": 102,
        "patient_id": 1002,
        "risk_score": 65,
        "risk_level": "Medium"
    },
    {
        "encounter_id": 103,
        "patient_id": 1003,
        "risk_score": 90,
        "risk_level": "High"
    }
]

@app.get("/encounters/{encounter_id}")
def get_encounter(encounter_id: int):
    for encounter in encounters:
        if encounter["encounter_id"] == encounter_id:
            return encounter

    raise HTTPException(
        status_code=404,
        detail="Encounter not found"
    )