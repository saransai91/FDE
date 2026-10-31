"""API layer: routing, status codes, validation and headers with services mocked (no DB)."""

from datetime import date, datetime
from unittest.mock import MagicMock

import pytest

from app.api.deps import get_employee_service, get_review_period_service, get_review_service
from app.errors import BusinessRuleError, ConflictError
from app.main import app
from app.schemas.employee import EmployeeOut
from app.schemas.review import ReviewFilters, ReviewOut
from app.schemas.review_period import ReviewPeriodOut

REVIEW = ReviewOut(
    id=1, employee_id=1, employee_code="EMP101", employee_name="John Smith", period_id=6,
    period_name="H1 2026", quality_rating=4, delivery_rating=5, teamwork_rating=4,
    average_rating=4.33, comments="Strong performer", created_at=datetime(2026, 1, 15, 10, 30),
)
VALID_BODY = dict(employee_id=1, period_id=6, quality_rating=4, delivery_rating=5,
                  teamwork_rating=4, comments="Strong performer")


@pytest.fixture
def review_service():
    service = MagicMock()
    app.dependency_overrides[get_review_service] = lambda: service
    return service


def test_root(client):
    assert client.get("/").status_code == 200


def test_swagger_docs_available(client):
    assert client.get("/api/docs").status_code == 200
    paths = client.get("/api/openapi.json").json()["paths"]
    assert {"/api/employees", "/api/review-periods", "/api/reviews"} <= set(paths)


# ---------- GET /api/employees ----------

def test_list_employees(client):
    service = MagicMock()
    service.list_employees.return_value = [EmployeeOut(
        id=1, employee_id="EMP101", name="John Smith", department="Engineering",
        email="j@x.com", status="Active")]
    app.dependency_overrides[get_employee_service] = lambda: service

    response = client.get("/api/employees", params={"status": "Active"})

    assert response.status_code == 200
    assert response.json()[0]["employee_id"] == "EMP101"
    service.list_employees.assert_called_once_with("Active")


def test_list_employees_rejects_bad_status(client):
    app.dependency_overrides[get_employee_service] = lambda: MagicMock()
    assert client.get("/api/employees", params={"status": "Gone"}).status_code == 422


# ---------- GET /api/review-periods ----------

def test_list_review_periods(client):
    service = MagicMock()
    service.list_periods.return_value = [ReviewPeriodOut(
        id=6, name="H1 2026", start_date=date(2026, 1, 1), end_date=date(2026, 6, 30), status="Open")]
    app.dependency_overrides[get_review_period_service] = lambda: service

    response = client.get("/api/review-periods", params={"status": "Open"})

    assert response.status_code == 200
    assert response.json() == [{"id": 6, "name": "H1 2026", "start_date": "2026-01-01",
                                "end_date": "2026-06-30", "status": "Open"}]
    service.list_periods.assert_called_once_with("Open")


def test_list_review_periods_rejects_bad_status(client):
    app.dependency_overrides[get_review_period_service] = lambda: MagicMock()
    assert client.get("/api/review-periods", params={"status": "Pending"}).status_code == 422


# ---------- GET /api/reviews ----------

def test_list_reviews_returns_array_and_total_header(client, review_service):
    review_service.list_reviews.return_value = ([REVIEW], 12)

    response = client.get("/api/reviews", params={"period_id": 6, "page": 2, "page_size": 5})

    assert response.status_code == 200
    assert response.headers["X-Total-Count"] == "12"
    body = response.json()
    assert body[0]["average_rating"] == 4.33
    assert body[0]["employee_name"] == "John Smith"
    review_service.list_reviews.assert_called_once_with(
        ReviewFilters(period_id=6, employee_id=None, page=2, page_size=5))


def test_list_reviews_default_paging(client, review_service):
    review_service.list_reviews.return_value = ([], 0)
    client.get("/api/reviews")
    review_service.list_reviews.assert_called_once_with(ReviewFilters(page=1, page_size=5))


@pytest.mark.parametrize("params", [{"page": 0}, {"page_size": 101}, {"period_id": "abc"}, {"employee_id": 0}])
def test_list_reviews_invalid_query(client, review_service, params):
    assert client.get("/api/reviews", params=params).status_code == 422
    review_service.list_reviews.assert_not_called()


# ---------- POST /api/reviews ----------

def test_create_review_201(client, review_service):
    review_service.create_review.return_value = REVIEW

    response = client.post("/api/reviews", json=VALID_BODY)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["average_rating"] == 4.33


@pytest.mark.parametrize(
    "override",
    [
        {"quality_rating": 0},
        {"delivery_rating": 6},
        {"teamwork_rating": 3.5},
        {"comments": "   "},
        {"employee_id": None},
        {"average_rating": 5},
    ],
)
def test_create_review_validation_422(client, review_service, override):
    response = client.post("/api/reviews", json={**VALID_BODY, **override})
    assert response.status_code == 422
    review_service.create_review.assert_not_called()


def test_create_review_business_rule_422(client, review_service):
    review_service.create_review.side_effect = BusinessRuleError("Review period H1 2025 is Closed")

    response = client.post("/api/reviews", json=VALID_BODY)

    assert response.status_code == 422
    assert response.json() == {"detail": "Review period H1 2025 is Closed"}


def test_create_review_duplicate_409(client, review_service):
    review_service.create_review.side_effect = ConflictError("A review already exists for this employee and period")

    response = client.post("/api/reviews", json=VALID_BODY)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_cors_exposes_total_count_header(client, review_service):
    review_service.list_reviews.return_value = ([], 0)
    response = client.get("/api/reviews", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "X-Total-Count" in response.headers["access-control-expose-headers"]
