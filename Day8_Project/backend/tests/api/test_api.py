"""API end-to-end tests: HTTP -> service -> repository -> Postgres test DB (rolled back per test)."""
import pytest

from tests.helpers import period_id

NEW_REVIEW = dict(employee_id="EMP111", quality_rating=4, delivery_rating=5,
                  teamwork_rating=4, comments="Ran a smooth sprint review.")


# ---------- employees ----------

def test_list_employees(client):
    res = client.get("/api/employees")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 12
    assert set(body[0]) == {"employee_id", "name", "department", "designation", "email", "status"}
    assert [e["name"] for e in body] == sorted(e["name"] for e in body)


def test_get_employee(client):
    res = client.get("/api/employees/EMP101")
    assert res.status_code == 200
    assert res.json()["name"] == "John Smith"


def test_get_employee_not_found(client):
    res = client.get("/api/employees/EMP999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"]


# ---------- review periods ----------

def test_list_review_periods(client):
    res = client.get("/api/review-periods")
    assert res.status_code == 200
    body = res.json()
    assert {p["period_type"] for p in body} == {"Annual", "Half-Yearly", "Quarterly"}
    assert all(p["status"] == "Open" for p in body)


# ---------- GET /reviews ----------

def test_list_all_reviews_default_page(client):
    res = client.get("/api/reviews")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 12
    assert body["page"] == 1 and body["page_size"] == 10 and body["total_pages"] == 2
    assert len(body["items"]) == 10
    created = [r["created_at"] for r in body["items"]]
    assert created == sorted(created, reverse=True)


def test_pagination_page_size_5(client):
    page1 = client.get("/api/reviews", params={"page_size": 5}).json()
    page3 = client.get("/api/reviews", params={"page_size": 5, "page": 3}).json()
    assert len(page1["items"]) == 5 and page1["total_pages"] == 3
    assert len(page3["items"]) == 2
    ids = {r["review_id"] for r in page1["items"]} & {r["review_id"] for r in page3["items"]}
    assert not ids


@pytest.mark.parametrize("size", [0, 3, 20])
def test_page_size_must_be_5_or_10(client, size):
    assert client.get("/api/reviews", params={"page_size": size}).status_code == 422


def test_filter_by_employee_returns_all_periods_and_average(client):
    body = client.get("/api/reviews", params={"employee_id": "EMP101"}).json()
    assert body["total"] == 3
    assert {r["employee_id"] for r in body["items"]} == {"EMP101"}
    assert {r["review_period_name"] for r in body["items"]} == {"FY 2025", "H1 2026", "Q3 2026"}
    # reviews averages: 4.00, 4.33, 4.67 -> mean 4.33
    assert body["average_rating"] == 4.33


def test_filter_by_period(client, db_session):
    body = client.get("/api/reviews", params={"review_period_id": period_id(db_session, "H1 2026")}).json()
    assert body["total"] == 6
    assert {r["review_period_name"] for r in body["items"]} == {"H1 2026"}


def test_filter_by_employee_and_period(client, db_session):
    body = client.get(
        "/api/reviews", params={"employee_id": "EMP101", "review_period_id": period_id(db_session, "Q3 2026")}
    ).json()
    assert body["total"] == 1
    r = body["items"][0]
    assert (r["quality_rating"], r["delivery_rating"], r["teamwork_rating"], r["average_rating"]) == (5, 5, 4, 4.67)


def test_filter_with_no_matches(client):
    body = client.get("/api/reviews", params={"employee_id": "EMP112"}).json()
    assert body == {"items": [], "total": 0, "page": 1, "page_size": 10, "total_pages": 0, "average_rating": None}


# ---------- GET /reviews/{id} ----------

def test_get_review_detail(client):
    first = client.get("/api/reviews", params={"employee_id": "EMP103"}).json()["items"][0]
    res = client.get(f"/api/reviews/{first['review_id']}")
    assert res.status_code == 200
    body = res.json()
    assert body["employee_name"] == "Michael Lee"
    assert body["department"] == "QA"
    assert body["comments"] == "Outstanding quality across all releases."
    assert body["average_rating"] == 5.0


def test_get_review_not_found(client):
    assert client.get("/api/reviews/999999").status_code == 404


# ---------- POST /reviews ----------

def test_submit_review(client, db_session):
    pid = period_id(db_session, "Q4 2026")
    res = client.post("/api/reviews", json={**NEW_REVIEW, "review_period_id": pid})
    assert res.status_code == 201
    body = res.json()
    assert body["message"] == "Review submitted successfully"
    review = body["review"]
    assert review["average_rating"] == 4.33
    assert review["employee_name"] == "Emily Davis"
    assert review["review_period_name"] == "Q4 2026"

    # it is now returned by search and detail
    listed = client.get("/api/reviews", params={"employee_id": "EMP111", "review_period_id": pid}).json()
    assert listed["total"] == 1
    assert client.get(f"/api/reviews/{review['review_id']}").status_code == 200


def test_submit_duplicate_review_returns_409(client, db_session):
    pid = period_id(db_session, "H1 2026")
    res = client.post("/api/reviews", json={**NEW_REVIEW, "employee_id": "EMP101", "review_period_id": pid})
    assert res.status_code == 409
    assert "already has a review" in res.json()["detail"]


def test_submit_unknown_employee_returns_422(client, db_session):
    res = client.post("/api/reviews", json={**NEW_REVIEW, "employee_id": "EMP999",
                                            "review_period_id": period_id(db_session, "Q4 2026")})
    assert res.status_code == 422


def test_submit_unknown_period_returns_422(client):
    res = client.post("/api/reviews", json={**NEW_REVIEW, "review_period_id": 9999})
    assert res.status_code == 422


@pytest.mark.parametrize("override", [{"quality_rating": 0}, {"delivery_rating": 6}, {"comments": "   "}, {"comments": None}])
def test_submit_invalid_body_returns_422(client, db_session, override):
    body = {**NEW_REVIEW, "review_period_id": period_id(db_session, "Q4 2026"), **override}
    assert client.post("/api/reviews", json=body).status_code == 422


# ---------- docs ----------

def test_swagger_and_openapi_available(client):
    assert client.get("/api/docs").status_code == 200
    paths = client.get("/api/openapi.json").json()["paths"]
    assert {"/api/employees", "/api/employees/{employee_id}", "/api/review-periods",
            "/api/reviews", "/api/reviews/{review_id}"} <= set(paths)
    assert {"get", "post"} <= set(paths["/api/reviews"])
