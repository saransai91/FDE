"""FastAPI dependency wiring: session -> repositories -> services."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import EmployeeRepository, ReviewPeriodRepository, ReviewRepository
from app.services import EmployeeService, ReviewPeriodService, ReviewService


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(EmployeeRepository(db))


def get_review_period_service(db: Session = Depends(get_db)) -> ReviewPeriodService:
    return ReviewPeriodService(ReviewPeriodRepository(db))


def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(ReviewRepository(db), EmployeeRepository(db), ReviewPeriodRepository(db))
