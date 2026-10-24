// Data the form sends to POST /encounters
export interface EncounterCreate {
  patient_id: number;
  age: string;
  time_in_hospital: number;
  number_inpatient: number;
  number_emergency: number;
  num_medications: number;
}

// An encounter as returned by the Python API (same fields as Day5, plus form inputs).
// risk_score / risk_level are null until a risk model scores the encounter.
export interface Encounter extends EncounterCreate {
  encounter_id: number;
  risk_score: number | null;
  risk_level: string | null;
}
