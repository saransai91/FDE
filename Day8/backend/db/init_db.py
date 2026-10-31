"""Create the database (if missing), apply schema.sql and load seed.sql.

Usage (from Day8/backend):
    .venv/Scripts/python db/init_db.py            # app DB, schema + seed
    .venv/Scripts/python db/init_db.py --no-seed  # schema only
"""

import argparse
import sys
from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings  # noqa: E402

DB_DIR = Path(__file__).resolve().parent


def _conninfo(url: str, dbname: str | None = None) -> str:
    u = make_url(url)
    return psycopg.conninfo.make_conninfo(
        host=u.host or "localhost",
        port=u.port or 5432,
        user=u.username,
        password=u.password,
        dbname=dbname or u.database,
    )


def create_database_if_missing(url: str) -> None:
    name = make_url(url).database
    with psycopg.connect(_conninfo(url, "postgres"), autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone()
        if not exists:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            print(f"Created database {name}")


def run_sql_file(url: str, path: Path) -> None:
    with psycopg.connect(_conninfo(url)) as conn:
        conn.execute(path.read_text(encoding="utf-8"))
    print(f"Applied {path.name}")


def init_db(url: str, seed: bool = True) -> None:
    create_database_if_missing(url)
    run_sql_file(url, DB_DIR / "schema.sql")
    if seed:
        run_sql_file(url, DB_DIR / "seed.sql")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-seed", action="store_true")
    args = parser.parse_args()
    init_db(settings.database_url, seed=not args.no_seed)
