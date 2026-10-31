from fastapi import APIRouter, Depends

from app.dependencies import get_employee_service
from app.schemas import EmployeeOut, ErrorOut
from app.services import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeOut], summary="List all employees")
def list_employees(service: EmployeeService = Depends(get_employee_service)):
    """All employees, sorted by name. Feeds the employee dropdowns."""
    return service.list()


@router.get(
    "/{employee_id}",
    response_model=EmployeeOut,
    summary="Get one employee",
    responses={404: {"model": ErrorOut}},
)
def get_employee(employee_id: str, service: EmployeeService = Depends(get_employee_service)):
    return service.get(employee_id)
