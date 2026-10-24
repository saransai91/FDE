// Body sent to POST /encounters when adding an encounter
export interface EncounterCreate {
  patient_id: number;
  age: string;
  time_in_hospital: number;
  number_inpatient: number;
  number_emergency: number;
  num_medications: number;
}

// Shape of one encounter returned by the FastAPI GET /encounters endpoint
export interface Encounter extends EncounterCreate {
  encounter_id: number;
  risk_score: number | null;
  risk_level: RiskLevel | null;
}

// Age groups the backend accepts, e.g. "[50-60)"
export const AGE_GROUPS = Array.from(
  { length: 10 },
  (_, i) => `[${i * 10}-${i * 10 + 10})`,
);

export type RiskLevel = "Low" | "Medium" | "High";
