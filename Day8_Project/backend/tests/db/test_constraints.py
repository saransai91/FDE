"""The database itself enforces the data rules, even if the API is bypassed (raw SQL)."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

INSERT = text(
    """
    INSERT INTO performance_reviews
        (employee_id, review_period_id, quality_rating, delivery_rating, teamwork_rating, average_rating, comments)
    VALUES (:emp, (SELECT review_period_id FROM review_periods WHERE name = :period), :q, :d, :t, :avg, :c)
    """
)
GOOD = dict(emp="EMP112", period="Q4 2026", q=3, d=3, t=3, avg=3, c="ok")


def insert(conn, **overrides):
    conn.execute(INSERT, {**GOOD, **overrides})


def test_valid_insert(raw_conn):
    insert(raw_conn)


@pytest.mark.parametrize("field,value", [("q", 0), ("d", 6), ("t", -1), ("avg", 5.5)])
def test_rating_check_constraints(raw_conn, field, value):
    with pytest.raises(IntegrityError):
        insert(raw_conn, **{field: value})


@pytest.mark.parametrize("comments", [None, "", "   "])
def test_comments_mandatory(raw_conn, comments):
    with pytest.raises(IntegrityError):
        insert(raw_conn, c=comments)


def test_one_review_per_employee_per_period(raw_conn):
    insert(raw_conn)
    with pytest.raises(IntegrityError, match="uq_review_employee_period"):
        insert(raw_conn)


def test_employee_must_exist(raw_conn):
    with pytest.raises(IntegrityError):
        insert(raw_conn, emp="EMP999")


def test_period_must_exist(raw_conn):
    with pytest.raises(IntegrityError):
        insert(raw_conn, period="No such period")


def test_period_end_date_after_start(raw_conn):
    with pytest.raises(IntegrityError, match="chk_period_dates"):
        raw_conn.execute(text(
            "INSERT INTO review_periods (name, period_type, start_date, end_date) "
            "VALUES ('Bad', 'Monthly', '2026-02-01', '2026-01-01')"
        ))


def test_period_type_restricted(raw_conn):
    with pytest.raises(IntegrityError):
        raw_conn.execute(text(
            "INSERT INTO review_periods (name, period_type, start_date, end_date) "
            "VALUES ('Weekly 1', 'Weekly', '2026-01-01', '2026-01-07')"
        ))


def test_employee_with_reviews_cannot_be_deleted(raw_conn):
    with pytest.raises(IntegrityError):
        raw_conn.execute(text("DELETE FROM employees WHERE employee_id = 'EMP101'"))
