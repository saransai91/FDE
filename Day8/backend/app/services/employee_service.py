from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeOut


class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    def list_employees(self, status: str | None = None) -> list[EmployeeOut]:
        return [EmployeeOut.model_validate(e) for e in self.employee_repo.list(status)]
