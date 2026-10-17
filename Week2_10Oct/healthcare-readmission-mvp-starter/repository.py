from database import get_connection

def list_encounters(limit: int, offset: int):
    with get_connection() as conn:
        return conn.execute(
            """SELECT * FROM patient_encounters
               ORDER BY risk_score DESC, encounter_id
               LIMIT %s OFFSET %s""",
            (limit, offset),
        ).fetchall()

def get_encounter(encounter_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM patient_encounters WHERE encounter_id = %s",
            (encounter_id,),
        ).fetchone()

def get_care_queue(limit: int, offset: int, high_only: bool = False):
    if high_only:
        condition = "risk_level = 'HIGH'"
    else:
        condition = "risk_level IN ('MEDIUM', 'HIGH')"
    # condition is selected only from these fixed strings, not user input.
    with get_connection() as conn:
        return conn.execute(
            f"""SELECT * FROM patient_encounters
                WHERE {condition}
                ORDER BY risk_score DESC, encounter_id
                LIMIT %s OFFSET %s""",
            (limit, offset),
        ).fetchall()

def update_intervention(encounter_id: int, fields: dict):
    allowed = {"status", "assigned_to", "notes"}
    fields = {key: value for key, value in fields.items() if key in allowed}
    with get_connection() as conn:
        exists = conn.execute(
            "SELECT encounter_id FROM patient_encounters WHERE encounter_id = %s",
            (encounter_id,),
        ).fetchone()
        if not exists:
            return None

        conn.execute(
            """INSERT INTO care_interventions (encounter_id)
               VALUES (%s)
               ON CONFLICT (encounter_id) DO NOTHING""",
            (encounter_id,),
        )

        if fields:
            assignments = ", ".join(f"{key} = %s" for key in fields)
            values = list(fields.values()) + [encounter_id]
            conn.execute(
                f"""UPDATE care_interventions
                    SET {assignments}, updated_at = NOW()
                    WHERE encounter_id = %s""",
                values,
            )

        return conn.execute(
            "SELECT * FROM care_interventions WHERE encounter_id = %s",
            (encounter_id,),
        ).fetchone()

def operations_summary():
    with get_connection() as conn:
        risk_counts = conn.execute(
            """SELECT risk_level, COUNT(*) AS count
               FROM patient_encounters GROUP BY risk_level"""
        ).fetchall()
        intervention_counts = conn.execute(
            """SELECT
                 COUNT(*) FILTER (WHERE status = 'PENDING_REVIEW') AS pending_interventions,
                 COUNT(*) FILTER (WHERE status = 'CLOSED') AS completed_interventions
               FROM care_interventions"""
        ).fetchone()
        total = conn.execute("SELECT COUNT(*) AS count FROM patient_encounters").fetchone()
    risks = {row["risk_level"]: row["count"] for row in risk_counts}
    return {
        "total_encounters": total["count"],
        "high_risk": risks.get("HIGH", 0),
        "medium_risk": risks.get("MEDIUM", 0),
        "low_risk": risks.get("LOW", 0),
        "pending_interventions": intervention_counts["pending_interventions"],
        "completed_interventions": intervention_counts["completed_interventions"],
    }

def readmission_analysis():
    # The outcome is used here only for evaluation, never for calculating risk_score.
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT risk_level,
                      COUNT(*) AS encounters,
                      COUNT(*) FILTER (WHERE readmitted = '<30') AS readmitted_under_30_days
               FROM patient_encounters
               GROUP BY risk_level
               ORDER BY CASE risk_level WHEN 'HIGH' THEN 1
                                        WHEN 'MEDIUM' THEN 2 ELSE 3 END"""
        ).fetchall()
    results = []
    for row in rows:
        count = row["encounters"]
        events = row["readmitted_under_30_days"]
        results.append({
            "risk_level": row["risk_level"],
            "encounters": count,
            "readmitted_under_30_days": events,
            "readmission_rate_percent": round(events * 100 / count, 2) if count else 0,
        })
    return {"groups": results}

def management_dashboard():
    summary = operations_summary()
    analysis = readmission_analysis()
    return {"operations": summary, "historical_readmission_analysis": analysis}
