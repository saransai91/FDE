from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_employee_service
from app.schemas.employee import EmployeeOut, EmployeeStatus
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeOut], summary="Get list of employees")
def list_employees(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
    status: EmployeeStatus | None = None,
):
    return service.list_employees(status)
