import type { Encounter } from "../types";
import PatientRow from "./PatientRow";

interface PatientTableProps {
  encounters: Encounter[];
  onDelete: (encounterId: number) => void;
}

function PatientTable({ encounters, onDelete }: PatientTableProps) {
  if (encounters.length === 0) {
    return <p>No encounters found.</p>;
  }

  return (
    <table className="patient-table">
      <thead>
        <tr>
          <th>Encounter ID</th>
          <th>Patient ID</th>
          <th>Age</th>
          <th>Days in Hospital</th>
          <th>Inpatient Visits</th>
          <th>Emergency Visits</th>
          <th>Medications</th>
          <th>Risk Score</th>
          <th>Risk Level</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {encounters.map((encounter) => (
          <PatientRow
            key={encounter.encounter_id}
            encounter={encounter}
            onDelete={onDelete}
          />
        ))}
      </tbody>
    </table>
  );
}

export default PatientTable;
