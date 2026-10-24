"""Data access for the encounter and intervention_update tables. All SQL lives here."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from models import (
    Encounter,
    HighCarePatient,
    InterventionUpdate,
    InterventionUpdateCreate,
    PatientSearch,
)

# Tests point this at a temporary file so they never touch the real database
DB_PATH = Path(os.environ.get("ENCOUNTER_DB", Path(__file__).parent / "encounters.db"))

SEED_ENCOUNTERS = [
    # encounter_id, patient_id, age, time_in_hospital, inpatient, emergency, medications, risk_score, risk_level
    (101, 1001, "[50-60)", 3, 0, 0, 12, 25, "Low"),
    (102, 1002, "[60-70)", 5, 1, 1, 18, 65, "Medium"),
    (103, 1003, "[70-80)", 9, 3, 2, 25, 90, "High"),
    (104, 1004, "[40-50)", 2, 0, 0, 8, 15, "Low"),
    (105, 1005, "[80-90)", 12, 4, 3, 30, 95, "High"),
    (106, 1006, "[60-70)", 6, 2, 0, 20, 72, "Medium"),
    (107, 1003, "[70-80)", 7, 2, 1, 22, 84, "High"),
    (108, 1007, "[30-40)", 1, 0, 0, 5, 10, "Low"),
    (109, 1008, "[70-80)", 10, 3, 1, 27, 88, "High"),
    (110, 1002, "[60-70)", 4, 1, 0, 16, 58, "Medium"),
]

SEED_UPDATES = [
    # encounter_id, status, assigned_to, notes, updated_at
    (103, "In Progress", "Nurse Priya", "Called patient, follow-up visit booked.", "2026-10-20T09:15:00"),
    (105, "In Progress", "Dr. Kumar", "Medication review started.", "2026-10-21T11:00:00"),
    (105, "Completed", "Dr. Kumar", "Insulin dose adjusted, patient educated.", "2026-10-22T16:30:00"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create both tables and seed them with sample rows on first run."""
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intervention_update (
                update_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                encounter_id INTEGER NOT NULL REFERENCES encounter(encounter_id),
                status       TEXT    NOT NULL,
                assigned_to  TEXT    NOT NULL DEFAULT '',
                notes        TEXT    NOT NULL DEFAULT '',
                updated_at   TEXT    NOT NULL
            )
            """
        )
        if conn.execute("SELECT COUNT(*) FROM encounter").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO encounter (encounter_id, patient_id, age, time_in_hospital,
                    number_inpatient, number_emergency, num_medications, risk_score, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                SEED_ENCOUNTERS,
            )
        if conn.execute("SELECT COUNT(*) FROM intervention_update").fetchone()[0] == 0:
            conn.executemany(
                """
                INSERT INTO intervention_update (encounter_id, status, assigned_to, notes, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                SEED_UPDATES,
            )


def find_encounter(encounter_id: int) -> Encounter | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM encounter WHERE encounter_id = ?", (encounter_id,)
        ).fetchone()
    return Encounter(**dict(row)) if row else None


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


def find_high_care_patients() -> list[HighCarePatient]:
    """High-risk encounters joined with their most recent intervention update (if any)."""
    sql = """
        SELECT e.*,
               COALESCE(i.status, 'Not Started') AS intervention_status,
               i.assigned_to,
               i.updated_at AS last_updated
        FROM encounter e
        LEFT JOIN intervention_update i ON i.update_id = (
            SELECT update_id FROM intervention_update
            WHERE encounter_id = e.encounter_id
            ORDER BY updated_at DESC, update_id DESC
            LIMIT 1
        )
        WHERE e.risk_level = 'High'
        ORDER BY e.risk_score DESC, e.encounter_id
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
    return [HighCarePatient(**dict(row)) for row in rows]


def find_intervention_updates(encounter_id: int) -> list[InterventionUpdate]:
    """An encounter's intervention history, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM intervention_update
            WHERE encounter_id = ?
            ORDER BY updated_at DESC, update_id DESC
            """,
            (encounter_id,),
        ).fetchall()
    return [InterventionUpdate(**dict(row)) for row in rows]


def insert_intervention_update(encounter_id: int, data: InterventionUpdateCreate) -> InterventionUpdate:
    updated_at = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO intervention_update (encounter_id, status, assigned_to, notes, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (encounter_id, data.status, data.assigned_to, data.notes, updated_at),
        )
        update_id = cursor.lastrowid
    return InterventionUpdate(
        update_id=update_id, encounter_id=encounter_id, updated_at=updated_at, **data.model_dump()
    )
