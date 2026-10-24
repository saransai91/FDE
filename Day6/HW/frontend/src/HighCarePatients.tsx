import { useEffect, useState } from "react";
import { getHighCarePatients } from "./api";
import type { HighCarePatient } from "./types";

interface Props {
  onSelectEncounter: (encounterId: number) => void;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export function statusClass(status: string): string {
  return `badge status-${status.toLowerCase().replace(" ", "-")}`;
}

function HighCarePatients({ onSelectEncounter }: Props) {
  const [patients, setPatients] = useState<HighCarePatient[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getHighCarePatients()
      .then(setPatients)
      .catch((err) => setError(`Could not load high care patients: ${err.message}`));
  }, []);

  return (
    <div className="table-card wide">
      <div className="card-header">High Care Patients</div>
      <p className="hint">High risk encounters and their latest intervention status. Click an Encounter Id to update it.</p>

      {error && <p className="error padded">{error}</p>}
      {patients?.length === 0 && <p className="empty">No high risk patients.</p>}

      {patients && patients.length > 0 && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Encounter Id</th>
              <th>Patient Number</th>
              <th>Age</th>
              <th>Risk Score</th>
              <th>Intervention Status</th>
              <th>Assigned To</th>
              <th>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {patients.map((p) => (
              <tr key={p.encounter_id}>
                <td>
                  <button className="link" onClick={() => onSelectEncounter(p.encounter_id)}>
                    {p.encounter_id}
                  </button>
                </td>
                <td>{p.patient_id}</td>
                <td>{p.age}</td>
                <td>{p.risk_score ?? "—"}</td>
                <td>
                  <span className={statusClass(p.intervention_status)}>{p.intervention_status}</span>
                </td>
                <td>{p.assigned_to || "—"}</td>
                <td>{p.last_updated ? formatDate(p.last_updated) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default HighCarePatients;
