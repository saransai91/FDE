from pathlib import Path
import pandas as pd
from database import get_connection
from service import calculate_risk

CSV_PATH = Path("data/diabetic_data.csv")
REQUIRED = [
    "encounter_id", "patient_nbr", "age", "time_in_hospital",
    "number_inpatient", "number_emergency", "number_outpatient",
    "num_medications", "num_lab_procedures",
    "discharge_disposition_id", "admission_type_id", "readmitted",
]
NUMERIC = [
    "encounter_id", "patient_nbr", "time_in_hospital", "number_inpatient",
    "number_emergency", "number_outpatient", "num_medications",
    "num_lab_procedures", "discharge_disposition_id", "admission_type_id",
]

def clean_integer(value, default=0):
    if pd.isna(value) or str(value).strip() in {"", "?"}:
        return default
    return int(float(value))

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find {CSV_PATH}. Put diabetic_data.csv in the data folder."
        )

    with CSV_PATH.open(encoding="utf-8-sig") as csv_file:
        header = csv_file.readline().strip().lower()
    if header in {"field;purpose", "field,purpose"}:
        raise ValueError(
            f"{CSV_PATH} contains a field-description sheet, not encounter data. "
            "Replace it with the course-provided diabetic_data.csv whose header "
            "contains columns such as encounter_id, patient_nbr, and readmitted."
        )

    df = pd.read_csv(CSV_PATH)
    missing = [column for column in REQUIRED if column not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    df = df[REQUIRED].copy()
    df = df.drop_duplicates(subset=["encounter_id"], keep="first")

    records = []
    for _, row in df.iterrows():
        encounter = row.to_dict()
        for column in NUMERIC:
            encounter[column] = clean_integer(encounter[column])

        # Assignment rule uses only utilization, stay and medication fields.
        score, level = calculate_risk(encounter)
        records.append((
            encounter["encounter_id"], encounter["patient_nbr"],
            None if pd.isna(encounter["age"]) else str(encounter["age"]),
            encounter["time_in_hospital"], encounter["number_inpatient"],
            encounter["number_emergency"], encounter["number_outpatient"],
            encounter["num_medications"], encounter["num_lab_procedures"],
            encounter["discharge_disposition_id"], encounter["admission_type_id"],
            None if pd.isna(encounter["readmitted"]) else str(encounter["readmitted"]),
            score, level,
        ))

    sql = """
        INSERT INTO patient_encounters (
            encounter_id, patient_nbr, age, time_in_hospital, number_inpatient,
            number_emergency, number_outpatient, num_medications,
            num_lab_procedures, discharge_disposition_id, admission_type_id,
            readmitted, risk_score, risk_level
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (encounter_id) DO UPDATE SET
            patient_nbr = EXCLUDED.patient_nbr,
            age = EXCLUDED.age,
            time_in_hospital = EXCLUDED.time_in_hospital,
            number_inpatient = EXCLUDED.number_inpatient,
            number_emergency = EXCLUDED.number_emergency,
            number_outpatient = EXCLUDED.number_outpatient,
            num_medications = EXCLUDED.num_medications,
            num_lab_procedures = EXCLUDED.num_lab_procedures,
            discharge_disposition_id = EXCLUDED.discharge_disposition_id,
            admission_type_id = EXCLUDED.admission_type_id,
            readmitted = EXCLUDED.readmitted,
            risk_score = EXCLUDED.risk_score,
            risk_level = EXCLUDED.risk_level
    """
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.executemany(sql, records)

    print(f"Loaded or updated {len(records)} unique encounters.")

if __name__ == "__main__":
    main()