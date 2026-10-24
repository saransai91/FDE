import type { Encounter, EncounterCreate } from "./Encounter";

const API_URL = "http://127.0.0.1:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json();
}

// POST /encounters — insert a new encounter into the encounter table
export async function createEncounter(data: EncounterCreate): Promise<Encounter> {
  const response = await fetch(`${API_URL}/encounters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const created = await handleResponse<Encounter>(response);
  console.log("Response from Python API (POST):", created);
  return created;
}

// GET /encounters/{id} — fetch one encounter
export async function getEncounter(encounterId: number): Promise<Encounter> {
  const response = await fetch(`${API_URL}/encounters/${encounterId}`);
  return handleResponse<Encounter>(response);
}

// GET /encounters — fetch all encounters
export async function getEncounters(): Promise<Encounter[]> {
  const response = await fetch(`${API_URL}/encounters`);
  return handleResponse<Encounter[]>(response);
}
