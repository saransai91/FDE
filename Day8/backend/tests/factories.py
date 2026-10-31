"""Small helpers that insert rows for DB-backed tests."""

from datetime import date, datetime
from decimal import Decimal
from itertools import count

from sqlalchemy.orm import Session

from app.models import Employee, PerformanceReview, ReviewPeriod

_seq = count(1)


def make_employee(db: Session, **overrides) -> Employee:
    n = next(_seq)
    employee = Employee(
        employee_id=f"T{n:04d}",
        name=f"Test Employee {n}",
        department="Engineering",
        email=f"test{n}@example.com",
        status="Active",
    )
    for key, value in overrides.items():
        setattr(employee, key, value)
    db.add(employee)
    db.flush()
    return employee


def make_period(db: Session, **overrides) -> ReviewPeriod:
    n = next(_seq)
    period = ReviewPeriod(
        name=f"P{n}",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 6, 30),
        status="Open",
    )
    for key, value in overrides.items():
        setattr(period, key, value)
    db.add(period)
    db.flush()
    return period


def make_review(db: Session, employee: Employee, period: ReviewPeriod, **overrides) -> PerformanceReview:
    review = PerformanceReview(
        employee_id=employee.id,
        period_id=period.id,
        quality_rating=4,
        delivery_rating=4,
        teamwork_rating=4,
        average_rating=Decimal("4.00"),
        comments="Good work",
        created_at=datetime(2026, 7, 1, 10, 0, 0),
    )
    for key, value in overrides.items():
        setattr(review, key, value)
    db.add(review)
    db.flush()
    return review
