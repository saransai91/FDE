from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

PeriodStatus = Literal["Open", "Closed"]


class ReviewPeriodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start_date: date
    end_date: date
    status: PeriodStatus
