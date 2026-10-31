"""Wires Session -> Repositories -> Services. Tests override these to inject mocks."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.review_period_repository import ReviewPeriodRepository
from app.repositories.review_repository import ReviewRepository
from app.services.employee_service import EmployeeService
from app.services.review_period_service import ReviewPeriodService
from app.services.review_service import ReviewService

DbSession = Annotated[Session, Depends(get_db)]


def get_employee_service(db: DbSession) -> EmployeeService:
    return EmployeeService(EmployeeRepository(db))


def get_review_period_service(db: DbSession) -> ReviewPeriodService:
    return ReviewPeriodService(ReviewPeriodRepository(db))


def get_review_service(db: DbSession) -> ReviewService:
    return ReviewService(ReviewRepository(db), EmployeeRepository(db), ReviewPeriodRepository(db))
