"""End-to-end: HTTP -> API -> Service -> Repository -> PostgreSQL test DB (rolled back)."""

import pytest

from tests.factories import make_employee, make_period, make_review

pytestmark = pytest.mark.db


def _body(employee, period, **overrides):
    body = dict(employee_id=employee.id, period_id=period.id, quality_rating=4,
                delivery_rating=5, teamwork_rating=4, comments="Strong performer")
    body.update(overrides)
    return body


def test_submit_then_list(db_client, db_session):
    employee, period = make_employee(db_session, name="John Smith"), make_period(db_session, name="H1 2099")

    created = db_client.post("/api/reviews", json=_body(employee, period))
    assert created.status_code == 201
    assert created.json()["average_rating"] == 4.33
    assert created.json()["employee_name"] == "John Smith"
    assert created.json()["period_name"] == "H1 2099"

    listed = db_client.get("/api/reviews", params={"period_id": period.id})
    assert listed.headers["X-Total-Count"] == "1"
    assert listed.json()[0]["id"] == created.json()["id"]


def test_duplicate_review_409(db_client, db_session):
    employee, period = make_employee(db_session), make_period(db_session)
    assert db_client.post("/api/reviews", json=_body(employee, period)).status_code == 201
    assert db_client.post("/api/reviews", json=_body(employee, period)).status_code == 409


def test_closed_period_422(db_client, db_session):
    employee, period = make_employee(db_session), make_period(db_session, status="Closed")
    response = db_client.post("/api/reviews", json=_body(employee, period))
    assert response.status_code == 422
    assert "Closed" in response.json()["detail"]


def test_inactive_employee_422(db_client, db_session):
    employee, period = make_employee(db_session, status="Inactive"), make_period(db_session)
    assert db_client.post("/api/reviews", json=_body(employee, period)).status_code == 422


def test_unknown_employee_422(db_client, db_session):
    period = make_period(db_session)
    response = db_client.post("/api/reviews", json=dict(
        employee_id=999999, period_id=period.id, quality_rating=3, delivery_rating=3,
        teamwork_rating=3, comments="x"))
    assert response.status_code == 422


def test_pagination_header_and_page_size(db_client, db_session):
    period = make_period(db_session)
    for _ in range(7):
        make_review(db_session, make_employee(db_session), period)

    page2 = db_client.get("/api/reviews", params={"period_id": period.id, "page": 2, "page_size": 5})

    assert page2.headers["X-Total-Count"] == "7"
    assert len(page2.json()) == 2


def test_master_data_endpoints(db_client, db_session):
    make_employee(db_session, status="Inactive")
    make_period(db_session, status="Closed")

    employees = db_client.get("/api/employees", params={"status": "Active"}).json()
    periods = db_client.get("/api/review-periods", params={"status": "Open"}).json()

    assert all(e["status"] == "Active" for e in employees)
    assert all(p["status"] == "Open" for p in periods)
