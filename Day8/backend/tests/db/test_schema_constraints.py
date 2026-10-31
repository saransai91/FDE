"""DB layer: schema.sql integrity rules hold even when the API is bypassed (raw SQL)."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

pytestmark = pytest.mark.db


@pytest.fixture
def ids(db_session):
    """One employee and one period inserted via raw SQL."""
    emp = db_session.execute(text(
        "INSERT INTO employees (employee_id, name, department, email) "
        "VALUES ('DB001', 'Db Test', 'QA', 'db001@example.com') RETURNING id")).scalar_one()
    per = db_session.execute(text(
        "INSERT INTO review_periods (name, start_date, end_date) "
        "VALUES ('DB H1', '2026-01-01', '2026-06-30') RETURNING id")).scalar_one()
    return {"emp": emp, "per": per}


def _insert_review(db, emp, per, q=4, d=4, t=4, avg=4.0, comments="ok"):
    db.execute(text(
        "INSERT INTO performance_reviews (employee_id, period_id, quality_rating, delivery_rating, "
        "teamwork_rating, average_rating, comments) VALUES (:e, :p, :q, :d, :t, :a, :c)"),
        dict(e=emp, p=per, q=q, d=d, t=t, a=avg, c=comments))


def test_defaults_applied(db_session, ids):
    status = db_session.execute(text("SELECT status FROM employees WHERE id = :i"), {"i": ids["emp"]}).scalar_one()
    period_status = db_session.execute(text("SELECT status FROM review_periods WHERE id = :i"), {"i": ids["per"]}).scalar_one()
    _insert_review(db_session, ids["emp"], ids["per"])
    created_at = db_session.execute(text("SELECT created_at FROM performance_reviews WHERE employee_id = :i"),
                                    {"i": ids["emp"]}).scalar_one()
    assert (status, period_status) == ("Active", "Open")
    assert created_at is not None


def test_valid_review_accepted(db_session, ids):
    _insert_review(db_session, ids["emp"], ids["per"], q=1, d=5, t=3, avg=3.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"q": 0}, {"q": 6}, {"d": 0}, {"d": 6}, {"t": 0}, {"t": 6},  # BR-1
        {"avg": 0.5}, {"avg": 5.5},
        {"comments": None}, {"comments": "   "},                      # BR-6
    ],
)
def test_review_check_constraints(db_session, ids, kwargs):
    with pytest.raises(IntegrityError):
        _insert_review(db_session, ids["emp"], ids["per"], **kwargs)


def test_one_review_per_employee_per_period(db_session, ids):  # BR-3
    _insert_review(db_session, ids["emp"], ids["per"])
    with pytest.raises(IntegrityError, match="uq_review_employee_period"):
        _insert_review(db_session, ids["emp"], ids["per"])


def test_review_foreign_keys(db_session, ids):
    with pytest.raises(IntegrityError):
        _insert_review(db_session, 999999, ids["per"])


def test_cannot_delete_employee_with_reviews(db_session, ids):
    _insert_review(db_session, ids["emp"], ids["per"])
    with pytest.raises(IntegrityError):
        db_session.execute(text("DELETE FROM employees WHERE id = :i"), {"i": ids["emp"]})


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO employees (employee_id, name, department, email, status) VALUES ('X1','n','d','x1@e.com','Retired')",
        "INSERT INTO employees (employee_id, name, department, email) VALUES ('DB001','n','d','other@e.com')",
        "INSERT INTO employees (employee_id, name, department, email) VALUES ('X2','n','d','db001@example.com')",
        "INSERT INTO employees (employee_id, department, email) VALUES ('X3','d','x3@e.com')",
        "INSERT INTO review_periods (name, start_date, end_date, status) VALUES ('X P','2026-01-01','2026-06-30','Pending')",
        "INSERT INTO review_periods (name, start_date, end_date) VALUES ('X Q','2026-06-30','2026-01-01')",  # BR-7
        "INSERT INTO review_periods (name, start_date, end_date) VALUES ('DB H1','2027-01-01','2027-06-30')",
    ],
    ids=["emp-status", "emp-code-unique", "emp-email-unique", "emp-name-required",
         "period-status", "period-dates", "period-name-unique"],
)
def test_master_table_constraints(db_session, ids, sql):
    with pytest.raises(IntegrityError):
        db_session.execute(text(sql))
