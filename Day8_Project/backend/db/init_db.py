"""Create the database (if missing) and apply schema.sql + seed.sql.

Usage (from backend/):
    python db/init_db.py            # create + seed the main DB if it has no tables yet
    python db/init_db.py --reset    # DROP all data and re-seed the main DB
    python db/init_db.py --test     # same as --reset, for TEST_DATABASE_URL

Data lives in Postgres, so it survives restarts. Running without --reset never deletes data.
"""
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import settings  # noqa: E402

DB_DIR = Path(__file__).resolve().parent


def create_database_if_missing(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": target.database}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{target.database}"'))
            print(f"Created database {target.database}")
    admin.dispose()


def apply_sql(url: str, *files: str) -> None:
    engine = create_engine(url)
    with engine.begin() as conn:
        for name in files:
            conn.exec_driver_sql((DB_DIR / name).read_text(encoding="utf-8"))
            print(f"Applied {name}")
    engine.dispose()


def tables_exist(url: str) -> bool:
    engine = create_engine(url)
    with engine.connect() as conn:
        found = conn.execute(text("SELECT to_regclass('public.performance_reviews')")).scalar()
    engine.dispose()
    return found is not None


def init(url: str, reset: bool = True) -> None:
    create_database_if_missing(url)
    if not reset and tables_exist(url):
        print("Tables already exist; keeping existing data (use --reset to re-seed).")
        return
    apply_sql(url, "schema.sql", "seed.sql")


if __name__ == "__main__":
    if "--test" in sys.argv:
        init(settings.test_database_url)
    else:
        init(settings.database_url, reset="--reset" in sys.argv)
