"""Pydantic models shared by the API, service and repository layers."""

from typing import Literal

from pydantic import BaseModel, Field

AGE_GROUPS = [f"[{i}-{i + 10})" for i in range(0, 100, 10)]

RiskLevel = Literal["Low", "Medium", "High"]


class EncounterCreate(BaseModel):
    """Data sent by the form when adding an encounter."""

    patient_id: int = Field(gt=0)
    age: str
    time_in_hospital: int = Field(ge=0)
    number_inpatient: int = Field(ge=0)
    number_emergency: int = Field(ge=0)
    num_medications: int = Field(ge=0)


class Encounter(EncounterCreate):
    """An encounter as stored in the encounter table."""

    encounter_id: int
    risk_score: float | None = None
    risk_level: str | None = None


class PatientSearch(BaseModel):
    """Optional filters for the patient search. Filters left as None are ignored."""

    patient_id: int | None = Field(default=None, gt=0)
    min_risk_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
