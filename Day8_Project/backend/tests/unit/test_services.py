"""Service-layer business rules, with repositories mocked (no DB needed)."""
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models import Employee, PerformanceReview, ReviewPeriod
from app.schemas import ReviewCreate
from app.services import EmployeeService, ReviewService, calculate_average


def make_employee(status="Active"):
    return Employee(
        employee_id="EMP101", name="John Smith", department="Engineering",
        designation="Developer", email="john@example.com", status=status,
    )


def make_period(status="Open"):
    return ReviewPeriod(
        review_period_id=2, name="H1 2026", period_type="Half-Yearly",
        start_date=date(2026, 1, 1), end_date=date(2026, 6, 30), status=status,
    )


def make_payload(**overrides):
    data = dict(employee_id="EMP101", review_period_id=2, quality_rating=4,
                delivery_rating=5, teamwork_rating=4, comments="  Great sprint.  ")
    data.update(overrides)
    return ReviewCreate(**data)


@pytest.fixture
def repos():
    reviews, employees, periods = MagicMock(), MagicMock(), MagicMock()
    employees.get.return_value = make_employee()
    periods.get.return_value = make_period()
    reviews.exists.return_value = False

    def add(review: PerformanceReview):
        review.review_id = 99
        review.created_at = datetime(2026, 10, 25, tzinfo=timezone.utc)
        review.employee = employees.get.return_value
        review.review_period = periods.get.return_value
        return review

    reviews.add.side_effect = add
    return reviews, employees, periods


@pytest.fixture
def service(repos):
    return ReviewService(*repos)


@pytest.mark.parametrize(
    "q,d,t,expected",
    [(1, 1, 1, "1.00"), (5, 5, 5, "5.00"), (4, 5, 4, "4.33"), (4, 5, 5, "4.67"), (3, 4, 4, "3.67"), (2, 3, 3, "2.67")],
)
def test_average_is_sum_divided_by_three_rounded_to_2dp(q, d, t, expected):
    assert calculate_average(q, d, t) == Decimal(expected)


def test_create_saves_review_with_computed_average(service, repos):
    result = service.create(make_payload())

    saved = repos[0].add.call_args.args[0]
    assert saved.average_rating == Decimal("4.33")
    assert saved.comments == "Great sprint."  # trimmed
    assert result.review_id == 99
    assert result.employee_name == "John Smith"
    assert result.review_period_name == "H1 2026"
    assert result.average_rating == 4.33


def test_create_rejects_unknown_employee(service, repos):
    repos[1].get.return_value = None
    with pytest.raises(BusinessRuleError, match="does not exist"):
        service.create(make_payload())
    repos[0].add.assert_not_called()


def test_create_rejects_inactive_employee(service, repos):
    repos[1].get.return_value = make_employee(status="Inactive")
    with pytest.raises(BusinessRuleError, match="not active"):
        service.create(make_payload())


def test_create_rejects_unknown_period(service, repos):
    repos[2].get.return_value = None
    with pytest.raises(BusinessRuleError, match="does not exist"):
        service.create(make_payload())


def test_create_rejects_closed_period(service, repos):
    repos[2].get.return_value = make_period(status="Closed")
    with pytest.raises(BusinessRuleError, match="closed"):
        service.create(make_payload())


def test_create_rejects_second_review_for_same_period(service, repos):
    repos[0].exists.return_value = True
    with pytest.raises(ConflictError, match="already has a review"):
        service.create(make_payload())
    repos[0].add.assert_not_called()


def test_create_maps_unique_violation_race_to_conflict(service, repos):
    repos[0].add.side_effect = IntegrityError("insert", {}, Exception("duplicate key"))
    with pytest.raises(ConflictError):
        service.create(make_payload())


def test_get_review_not_found(service, repos):
    repos[0].get.return_value = None
    with pytest.raises(NotFoundError):
        service.get(123)


def test_search_builds_page_and_overall_average(service, repos):
    repos[0].stats.return_value = (12, Decimal("3.8611111"))
    repos[0].search.return_value = []

    page = service.search("EMP101", None, page=2, page_size=5)

    repos[0].search.assert_called_once_with("EMP101", None, 5, 5)  # offset = (page-1)*size
    assert page.total == 12
    assert page.total_pages == 3
    assert page.average_rating == 3.86


def test_search_with_no_results(service, repos):
    repos[0].stats.return_value = (0, None)
    repos[0].search.return_value = []

    page = service.search(None, 7, page=1, page_size=10)

    assert page.total == 0
    assert page.total_pages == 0
    assert page.average_rating is None


def test_get_employee_not_found():
    employees = MagicMock()
    employees.get.return_value = None
    with pytest.raises(NotFoundError):
        EmployeeService(employees).get("EMP999")
