export const RISK_LEVELS = ["Low", "Medium", "High"] as const;
export type RiskLevel = (typeof RISK_LEVELS)[number];

export const INTERVENTION_STATUSES = ["Not Started", "In Progress", "Completed", "Cancelled"] as const;
export type InterventionStatus = (typeof INTERVENTION_STATUSES)[number];

// An encounter as returned by the Python API
export interface Encounter {
  encounter_id: number;
  patient_id: number;
  age: string;
  time_in_hospital: number;
  number_inpatient: number;
  number_emergency: number;
  num_medications: number;
  risk_score: number | null;
  risk_level: RiskLevel | null;
}

// Query filters for GET /encounters/search — leave a field out to ignore it
export interface PatientSearch {
  patient_id?: number;
  min_risk_score?: number;
  risk_level?: RiskLevel;
}

// GET /patients/high-care — a high-risk encounter plus its latest intervention status
export interface HighCarePatient extends Encounter {
  intervention_status: InterventionStatus;
  assigned_to: string | null;
  last_updated: string | null;
}

// Body for POST /encounters/{id}/interventions
export interface InterventionUpdateCreate {
  status: InterventionStatus;
  assigned_to: string;
  notes: string;
}

export interface InterventionUpdate extends InterventionUpdateCreate {
  update_id: number;
  encounter_id: number;
  updated_at: string;
}
