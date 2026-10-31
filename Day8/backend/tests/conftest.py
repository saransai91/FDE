"""Shared fixtures.

DB-backed tests use a separate database (default: <app db>_test), recreated from
db/schema.sql once per test run. Every test runs inside a transaction that is rolled
back afterwards, so tests never see each other's data. If PostgreSQL is not reachable
the DB tests are skipped and the mocked unit tests still run.
"""

import sys
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.main import app

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "db"))
from init_db import init_db  # noqa: E402


def _test_database_url() -> str:
    if settings.test_database_url:
        return settings.test_database_url
    url = make_url(settings.database_url)
    return url.set(database=f"{url.database}_test").render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    url = _test_database_url()
    try:
        init_db(url, seed=False)
    except psycopg.OperationalError as exc:
        pytest.skip(f"PostgreSQL test database not available: {exc}".splitlines()[0])
    engine = create_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    connection = db_engine.connect()
    transaction = connection.begin()
    # Repository commit() calls only release a SAVEPOINT; the outer transaction is rolled back
    session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_client(db_session: Session) -> Iterator[TestClient]:
    """TestClient wired to the real (rolled-back) test DB session."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
