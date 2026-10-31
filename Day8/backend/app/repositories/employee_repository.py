from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, status: str | None = None) -> list[Employee]:
        stmt = select(Employee).order_by(Employee.employee_id)
        if status is not None:
            stmt = stmt.where(Employee.status == status)
        return list(self.db.scalars(stmt))

    def get(self, employee_pk: int) -> Employee | None:
        return self.db.get(Employee, employee_pk)
