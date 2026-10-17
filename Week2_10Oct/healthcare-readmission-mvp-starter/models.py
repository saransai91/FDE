from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

InterventionStatus = Literal[
    "PENDING_REVIEW",
    "ASSIGNED",
    "CONTACTED",
    "FOLLOW_UP_SCHEDULED",
    "CLOSED",
]

class InterventionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: InterventionStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=100)
    notes: str | None = None
