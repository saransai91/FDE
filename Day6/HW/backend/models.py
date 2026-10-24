"""Pydantic models shared by the API, service and repository layers."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["Low", "Medium", "High"]

InterventionStatus = Literal["Not Started", "In Progress", "Completed", "Cancelled"]


class Encounter(BaseModel):
    """An encounter as stored in the encounter table."""

    encounter_id: int
    patient_id: int
    age: str
    time_in_hospital: int
    number_inpatient: int
    number_emergency: int
    num_medications: int
    risk_score: float | None = None
    risk_level: RiskLevel | None = None


class PatientSearch(BaseModel):
    """Optional filters for the patient search. Filters left as None are ignored."""

    patient_id: int | None = Field(default=None, gt=0)
    min_risk_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None


class HighCarePatient(Encounter):
    """A high-risk encounter with its latest intervention status."""

    intervention_status: InterventionStatus = "Not Started"
    assigned_to: str | None = None
    last_updated: datetime | None = None


class InterventionUpdateCreate(BaseModel):
    """Data sent by the status tracking screen."""

    status: InterventionStatus
    assigned_to: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=500)


class InterventionUpdate(InterventionUpdateCreate):
    """One row of an encounter's intervention history."""

    update_id: int
    encounter_id: int
    updated_at: datetime
