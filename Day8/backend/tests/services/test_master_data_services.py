"""Service layer: employees and review periods (repositories mocked)."""

from datetime import date
from unittest.mock import MagicMock

from app.models import Employee, ReviewPeriod
from app.services.employee_service import EmployeeService
from app.services.review_period_service import ReviewPeriodService


def test_list_employees_maps_models_and_passes_status():
    repo = MagicMock()
    repo.list.return_value = [Employee(id=1, employee_id="EMP101", name="John Smith",
                                       department="Engineering", email="j@x.com", status="Active")]

    result = EmployeeService(repo).list_employees("Active")

    repo.list.assert_called_once_with("Active")
    assert result[0].employee_id == "EMP101"
    assert result[0].status == "Active"


def test_list_periods_maps_models_and_passes_status():
    repo = MagicMock()
    repo.list.return_value = [ReviewPeriod(id=6, name="H1 2026", start_date=date(2026, 1, 1),
                                           end_date=date(2026, 6, 30), status="Open")]

    result = ReviewPeriodService(repo).list_periods(None)

    repo.list.assert_called_once_with(None)
    assert result[0].name == "H1 2026"
    assert result[0].end_date == date(2026, 6, 30)
