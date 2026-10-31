"""Repository layer against the real PostgreSQL test DB (each test rolled back)."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.errors import ConflictError
from app.models import PerformanceReview
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.review_period_repository import ReviewPeriodRepository
from app.repositories.review_repository import ReviewRepository
from tests.factories import make_employee, make_period, make_review

pytestmark = pytest.mark.db


# ---------- EmployeeRepository ----------

def test_employee_list_ordered_and_filtered(db_session):
    b = make_employee(db_session, employee_id="ZZ02", status="Inactive")
    a = make_employee(db_session, employee_id="ZZ01")
    repo = EmployeeRepository(db_session)

    codes = [e.employee_id for e in repo.list()]
    assert codes.index("ZZ01") < codes.index("ZZ02")
    assert a in repo.list("Active") and b not in repo.list("Active")
    assert b in repo.list("Inactive")


def test_employee_get(db_session):
    employee = make_employee(db_session)
    repo = EmployeeRepository(db_session)
    assert repo.get(employee.id).email == employee.email
    assert repo.get(999999) is None


# ---------- ReviewPeriodRepository ----------

def test_period_list_newest_first_and_filtered(db_session):
    old = make_period(db_session, start_date=date(2001, 1, 1), end_date=date(2001, 6, 30), status="Closed")
    new = make_period(db_session, start_date=date(2099, 1, 1), end_date=date(2099, 6, 30))
    repo = ReviewPeriodRepository(db_session)

    periods = repo.list()
    assert periods.index(new) < periods.index(old)
    assert old not in repo.list("Open") and new in repo.list("Open")


def test_period_get(db_session):
    period = make_period(db_session)
    repo = ReviewPeriodRepository(db_session)
    assert repo.get(period.id).name == period.name
    assert repo.get(999999) is None


# ---------- ReviewRepository ----------

def test_review_create_returns_row_with_relations(db_session):
    employee, period = make_employee(db_session), make_period(db_session)

    review = ReviewRepository(db_session).create(PerformanceReview(
        employee_id=employee.id, period_id=period.id, quality_rating=4, delivery_rating=5,
        teamwork_rating=4, average_rating=Decimal("4.33"), comments="Great"))

    assert review.id is not None
    assert review.created_at is not None  # DB default NOW()
    assert review.average_rating == Decimal("4.33")
    assert review.employee.name == employee.name
    assert review.period.name == period.name


def test_review_create_duplicate_raises_conflict(db_session):
    employee, period = make_employee(db_session), make_period(db_session)
    make_review(db_session, employee, period)

    with pytest.raises(ConflictError):
        ReviewRepository(db_session).create(PerformanceReview(
            employee_id=employee.id, period_id=period.id, quality_rating=1, delivery_rating=1,
            teamwork_rating=1, average_rating=Decimal("1.00"), comments="dup"))


def test_review_exists_for(db_session):
    employee, period, other_period = make_employee(db_session), make_period(db_session), make_period(db_session)
    make_review(db_session, employee, period)
    repo = ReviewRepository(db_session)

    assert repo.exists_for(employee.id, period.id) is True
    assert repo.exists_for(employee.id, other_period.id) is False


def test_review_list_filters_and_count(db_session):
    e1, e2 = make_employee(db_session), make_employee(db_session)
    p1, p2 = make_period(db_session), make_period(db_session)
    make_review(db_session, e1, p1)
    make_review(db_session, e2, p1)
    make_review(db_session, e1, p2)
    repo = ReviewRepository(db_session)

    assert repo.count(period_id=p1.id) == 2
    assert repo.count(employee_id=e1.id) == 2
    assert repo.count(period_id=p1.id, employee_id=e1.id) == 1
    assert {r.employee_id for r in repo.list(period_id=p1.id, limit=10)} == {e1.id, e2.id}
    assert repo.list(period_id=p2.id, employee_id=e2.id) == []


def test_review_list_newest_first_with_paging(db_session):
    period = make_period(db_session)
    reviews = [
        make_review(db_session, make_employee(db_session), period, created_at=datetime(2026, 7, day))
        for day in range(1, 8)
    ]
    repo = ReviewRepository(db_session)

    page1 = repo.list(period_id=period.id, offset=0, limit=5)
    page2 = repo.list(period_id=period.id, offset=5, limit=5)

    assert [r.id for r in page1] == [r.id for r in reversed(reviews)][:5]
    assert [r.id for r in page2] == [reviews[1].id, reviews[0].id]
