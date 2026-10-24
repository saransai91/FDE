import type { Encounter } from "../types";

interface PatientRowProps {
  encounter: Encounter;
  onDelete: (encounterId: number) => void;
}

function PatientRow({ encounter, onDelete }: PatientRowProps) {
  const level = encounter.risk_level ?? "Unknown";

  return (
    <tr>
      <td>{encounter.encounter_id}</td>
      <td>{encounter.patient_id}</td>
      <td>{encounter.age}</td>
      <td>{encounter.time_in_hospital}</td>
      <td>{encounter.number_inpatient}</td>
      <td>{encounter.number_emergency}</td>
      <td>{encounter.num_medications}</td>
      <td>{encounter.risk_score ?? "-"}</td>
      <td>
        <span className={`badge badge-${level.toLowerCase()}`}>{level}</span>
      </td>
      <td>
        <button
          className="delete-button"
          onClick={() => onDelete(encounter.encounter_id)}
        >
          Delete
        </button>
      </td>
    </tr>
  );
}

export default PatientRow;
