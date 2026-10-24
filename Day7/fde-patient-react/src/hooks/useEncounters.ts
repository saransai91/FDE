import { useState, useEffect, useCallback } from "react";
import type { Encounter, EncounterCreate } from "../types";

const API_URL = "http://localhost:8000";

// Reads the FastAPI error detail if there is one, otherwise the status code
async function getErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // body wasn't JSON
  }
  return `Request failed with status ${response.status}`;
}

async function requestEncounters(): Promise<Encounter[]> {
  const response = await fetch(`${API_URL}/encounters`);
  if (!response.ok) throw new Error(await getErrorMessage(response));
  return response.json();
}

// Fetches, creates and deletes encounters, keeping the local list in sync
function useEncounters() {
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State is only set in the callbacks, after the request finishes
  const loadEncounters = useCallback(() => {
    return requestEncounters()
      .then((data) => {
        setEncounters(data);
        setError(null);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadEncounters();
  }, [loadEncounters]);

  const refresh = () => {
    setLoading(true);
    setError(null);
    loadEncounters();
  };

  // Returns true on success so the caller can e.g. reset its form
  const createEncounter = async (data: EncounterCreate): Promise<boolean> => {
    setError(null);
    try {
      const response = await fetch(`${API_URL}/encounters`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const created: Encounter = await response.json();
      setEncounters((prev) => [...prev, created]);
      return true;
    } catch (err) {
      setError((err as Error).message);
      return false;
    }
  };

  const deleteEncounter = async (encounterId: number): Promise<boolean> => {
    setError(null);
    try {
      const response = await fetch(`${API_URL}/encounters/${encounterId}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      setEncounters((prev) =>
        prev.filter((e) => e.encounter_id !== encounterId),
      );
      return true;
    } catch (err) {
      setError((err as Error).message);
      return false;
    }
  };

  return {
    encounters,
    loading,
    error,
    refresh,
    createEncounter,
    deleteEncounter,
  };
}

export default useEncounters;
