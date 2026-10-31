from typing import Literal

from pydantic import BaseModel, ConfigDict

EmployeeStatus = Literal["Active", "Inactive"]


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    name: str
    department: str
    email: str
    status: EmployeeStatus
