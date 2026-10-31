"""Shared fixtures.

DB-backed tests use TEST_DATABASE_URL. The test DB is rebuilt from schema.sql + seed.sql
once per run, and every test runs inside a transaction that is rolled back afterwards.
If Postgres is unreachable, DB-backed tests are skipped.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.main import app
from db.init_db import init


@pytest.fixture(scope="session")
def engine():
    try:
        init(settings.test_database_url)
    except OperationalError as exc:
        pytest.skip(f"Postgres not reachable: {exc.orig}")
    eng = create_engine(settings.test_database_url)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    conn = engine.connect()
    outer = conn.begin()
    # Service commits become SAVEPOINT releases, so the outer rollback undoes everything.
    session = Session(bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield session
    session.close()
    outer.rollback()
    conn.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def raw_conn(engine):
    """A plain connection in a transaction, for raw-SQL constraint tests."""
    conn = engine.connect()
    tx = conn.begin()
    yield conn
    tx.rollback()
    conn.close()
