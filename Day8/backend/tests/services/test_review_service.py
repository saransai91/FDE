"""Service layer: business rules with all repositories mocked (no DB)."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.errors import BusinessRuleError, ConflictError
from app.models import Employee, PerformanceReview, ReviewPeriod
from app.schemas.review import ReviewCreate, ReviewFilters
from app.services.review_service import ReviewService, calculate_average

ACTIVE_EMPLOYEE = Employee(id=1, employee_id="EMP101", name="John Smith", department="Eng",
                           email="j@x.com", status="Active")
OPEN_PERIOD = ReviewPeriod(id=6, name="H1 2026", start_date=date(2026, 1, 1),
                           end_date=date(2026, 6, 30), status="Open")


def _payload(**overrides) -> ReviewCreate:
    data = dict(employee_id=1, period_id=6, quality_rating=4, delivery_rating=5,
                teamwork_rating=4, comments="Strong performer")
    data.update(overrides)
    return ReviewCreate(**data)


def _saved(review: PerformanceReview) -> PerformanceReview:
    """Simulates what the repository returns after INSERT."""
    review.id = 1
    review.created_at = datetime(2026, 1, 15, 10, 30)
    review.employee = ACTIVE_EMPLOYEE
    review.period = OPEN_PERIOD
    return review


@pytest.fixture
def repos():
    review_repo, employee_repo, period_repo = MagicMock(), MagicMock(), MagicMock()
    employee_repo.get.return_value = ACTIVE_EMPLOYEE
    period_repo.get.return_value = OPEN_PERIOD
    review_repo.exists_for.return_value = False
    review_repo.create.side_effect = _saved
    return review_repo, employee_repo, period_repo


@pytest.fixture
def service(repos) -> ReviewService:
    return ReviewService(*repos)


@pytest.mark.parametrize(
    ("q", "d", "t", "expected"),
    [
        (4, 5, 4, "4.33"),
        (3, 4, 4, "3.67"),
        (5, 5, 5, "5.00"),
        (1, 1, 1, "1.00"),
        (2, 3, 3, "2.67"),
        (1, 1, 2, "1.33"),
    ],
)
def test_calculate_average_rounds_to_two_decimals(q, d, t, expected):
    assert calculate_average(q, d, t) == Decimal(expected)


def test_create_review_saves_with_server_calculated_average(service, repos):
    review_repo, _, _ = repos

    result = service.create_review(_payload())

    saved: PerformanceReview = review_repo.create.call_args.args[0]
    assert saved.average_rating == Decimal("4.33")
    assert saved.comments == "Strong performer"
    assert result.average_rating == 4.33
    assert result.employee_name == "John Smith"
    assert result.period_name == "H1 2026"


def test_create_review_unknown_employee(service, repos):
    repos[1].get.return_value = None
    with pytest.raises(BusinessRuleError, match="Employee 1 does not exist"):
        service.create_review(_payload())
    repos[0].create.assert_not_called()


def test_create_review_inactive_employee(service, repos):
    repos[1].get.return_value = Employee(id=1, employee_id="EMP124", name="X", department="Eng",
                                         email="x@x.com", status="Inactive")
    with pytest.raises(BusinessRuleError, match="EMP124 is Inactive"):
        service.create_review(_payload())
    repos[0].create.assert_not_called()


def test_create_review_unknown_period(service, repos):
    repos[2].get.return_value = None
    with pytest.raises(BusinessRuleError, match="Review period 6 does not exist"):
        service.create_review(_payload())


def test_create_review_closed_period(service, repos):
    repos[2].get.return_value = ReviewPeriod(id=3, name="H1 2025", start_date=date(2025, 1, 1),
                                             end_date=date(2025, 6, 30), status="Closed")
    with pytest.raises(BusinessRuleError, match="H1 2025 is Closed"):
        service.create_review(_payload())
    repos[0].create.assert_not_called()


def test_create_review_duplicate(service, repos):
    repos[0].exists_for.return_value = True
    with pytest.raises(ConflictError):
        service.create_review(_payload())
    repos[0].exists_for.assert_called_once_with(1, 6)
    repos[0].create.assert_not_called()


def test_list_reviews_passes_filters_and_offset(service, repos):
    review_repo = repos[0]
    review_repo.count.return_value = 12
    review_repo.list.return_value = [_saved(PerformanceReview(
        employee_id=1, period_id=6, quality_rating=4, delivery_rating=5, teamwork_rating=4,
        average_rating=Decimal("4.33"), comments="ok"))]

    items, total = service.list_reviews(ReviewFilters(period_id=6, employee_id=1, page=3, page_size=5))

    assert total == 12
    assert len(items) == 1 and items[0].employee_code == "EMP101"
    review_repo.count.assert_called_once_with(6, 1)
    review_repo.list.assert_called_once_with(period_id=6, employee_id=1, offset=10, limit=5)


def test_list_reviews_empty(service, repos):
    repos[0].count.return_value = 0
    repos[0].list.return_value = []
    assert service.list_reviews(ReviewFilters()) == ([], 0)
