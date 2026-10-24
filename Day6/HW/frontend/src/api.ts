import type {
  Encounter,
  HighCarePatient,
  InterventionUpdate,
  InterventionUpdateCreate,
  PatientSearch,
} from "./types";

export const API_URL = "http://127.0.0.1:8001";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    // FastAPI sends a string for our own errors and a list for validation errors
    const detail = Array.isArray(body?.detail)
      ? body.detail.map((d: { msg: string }) => d.msg).join("; ")
      : body?.detail;
    throw new Error(detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}

// GET /encounters/search — any combination of patient id, min risk score, risk level
export async function searchPatients(filters: PatientSearch): Promise<Encounter[]> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") params.append(key, String(value));
  }
  const response = await fetch(`${API_URL}/encounters/search?${params}`);
  return handleResponse<Encounter[]>(response);
}

// GET /encounters/{id} — fetch one encounter
export async function getEncounter(encounterId: number): Promise<Encounter> {
  const response = await fetch(`${API_URL}/encounters/${encounterId}`);
  return handleResponse<Encounter>(response);
}

// GET /patients/high-care — high-risk encounters with their latest intervention status
export async function getHighCarePatients(): Promise<HighCarePatient[]> {
  const response = await fetch(`${API_URL}/patients/high-care`);
  return handleResponse<HighCarePatient[]>(response);
}

// GET /encounters/{id}/interventions — status history, newest first
export async function getInterventionHistory(encounterId: number): Promise<InterventionUpdate[]> {
  const response = await fetch(`${API_URL}/encounters/${encounterId}/interventions`);
  return handleResponse<InterventionUpdate[]>(response);
}

// POST /encounters/{id}/interventions — record a new intervention status
export async function updateInterventionStatus(
  encounterId: number,
  data: InterventionUpdateCreate
): Promise<InterventionUpdate> {
  const response = await fetch(`${API_URL}/encounters/${encounterId}/interventions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<InterventionUpdate>(response);
}
