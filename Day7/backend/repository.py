"""Data access for the encounter table. All SQL lives here."""

import sqlite3
from pathlib import Path

from models import Encounter, EncounterCreate, PatientSearch

DB_PATH = Path(__file__).parent / "encounters.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the encounter table and seed it with the Day5 sample rows."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS encounter (
                encounter_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id       INTEGER NOT NULL,
                age              TEXT    NOT NULL,
                time_in_hospital INTEGER NOT NULL,
                number_inpatient INTEGER NOT NULL,
                number_emergency INTEGER NOT NULL,
                num_medications  INTEGER NOT NULL,
                risk_score       REAL,
                risk_level       TEXT
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM encounter").fetchone()[0]
        if count == 0:
            conn.executemany(
                """
                INSERT INTO encounter (encounter_id, patient_id, age, time_in_hospital,
                    number_inpatient, number_emergency, num_medications, risk_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (101, 1001, "[50-60)", 3, 0, 0, 12, 25, "Low"),
                    (102, 1002, "[60-70)", 5, 1, 1, 18, 65, "Medium"),
                    (103, 1003, "[70-80)", 9, 3, 2, 25, 90, "High"),
                ],
            )


def insert_encounter(data: EncounterCreate) -> int:
    """Insert a new encounter and return its generated encounter_id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO encounter (patient_id, age, time_in_hospital,
                number_inpatient, number_emergency, num_medications)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.patient_id,
                data.age,
                data.time_in_hospital,
                data.number_inpatient,
                data.number_emergency,
                data.num_medications,
            ),
        )
        return cursor.lastrowid


def find_encounter(encounter_id: int) -> Encounter | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM encounter WHERE encounter_id = ?", (encounter_id,)
        ).fetchone()
    return Encounter(**dict(row)) if row else None


def delete_encounter(encounter_id: int) -> bool:
    """Delete an encounter. Returns False if no row had that id."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM encounter WHERE encounter_id = ?", (encounter_id,)
        )
        return cursor.rowcount > 0


def find_all_encounters() -> list[Encounter]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM encounter ORDER BY encounter_id").fetchall()
    return [Encounter(**dict(row)) for row in rows]


def search_encounters(filters: PatientSearch) -> list[Encounter]:
    """Return encounters matching every filter that is set (AND), highest risk first."""
    conditions: list[str] = []
    params: list[object] = []

    if filters.patient_id is not None:
        conditions.append("patient_id = ?")
        params.append(filters.patient_id)
    if filters.min_risk_score is not None:
        conditions.append("risk_score >= ?")
        params.append(filters.min_risk_score)
    if filters.risk_level is not None:
        conditions.append("risk_level = ?")
        params.append(filters.risk_level)

    sql = "SELECT * FROM encounter"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY risk_score IS NULL, risk_score DESC, encounter_id"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [Encounter(**dict(row)) for row in rows]
