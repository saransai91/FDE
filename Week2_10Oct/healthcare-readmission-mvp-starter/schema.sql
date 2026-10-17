CREATE TABLE IF NOT EXISTS patient_encounters (
    encounter_id BIGINT PRIMARY KEY,
    patient_nbr BIGINT,
    age VARCHAR(50),
    time_in_hospital INTEGER NOT NULL,
    number_inpatient INTEGER NOT NULL,
    number_emergency INTEGER NOT NULL,
    number_outpatient INTEGER NOT NULL,
    num_medications INTEGER NOT NULL,
    num_lab_procedures INTEGER,
    discharge_disposition_id INTEGER,
    admission_type_id INTEGER,
    readmitted VARCHAR(20),
    risk_score INTEGER NOT NULL,
    risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH'))
);

CREATE TABLE IF NOT EXISTS care_interventions (
    intervention_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    encounter_id BIGINT NOT NULL UNIQUE
        REFERENCES patient_encounters(encounter_id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING_REVIEW'
        CHECK (status IN ('PENDING_REVIEW', 'ASSIGNED', 'CONTACTED',
                          'FOLLOW_UP_SCHEDULED', 'CLOSED')),
    assigned_to VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patient_encounters_risk
    ON patient_encounters (risk_level, risk_score DESC);
