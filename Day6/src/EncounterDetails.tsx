import { useEffect, useState } from "react";
import type { Encounter } from "./Encounter";
import { createEncounter, getEncounter, getEncounters } from "./api";
import "./EncounterDetails.css";

const AGE_GROUPS = [
  "[0-10)",
  "[10-20)",
  "[20-30)",
  "[30-40)",
  "[40-50)",
  "[50-60)",
  "[60-70)",
  "[70-80)",
  "[80-90)",
  "[90-100)",
];

function EncounterDetails() {
  const [patientNumber, setPatientNumber] = useState("");
  const [age, setAge] = useState("");
  const [timeInHospital, setTimeInHospital] = useState("");
  const [inpatientVisits, setInpatientVisits] = useState("");
  const [emergencyVisits, setEmergencyVisits] = useState("");
  const [medications, setMedications] = useState("");

  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [created, setCreated] = useState<Encounter | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Load existing encounters from the Python API
  useEffect(() => {
    getEncounters()
      .then(setEncounters)
      .catch((err) => setError(`Could not load encounters: ${err.message}`));
  }, []);

  const resetForm = () => {
    setPatientNumber("");
    setAge("");
    setTimeInHospital("");
    setInpatientVisits("");
    setEmergencyVisits("");
    setMedications("");
  };

  // Send the form to the API, then GET the new encounter back to confirm it was saved
  const addEncounter = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!patientNumber || !age) {
      setError("Patient Number and Age are required.");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      const { encounter_id } = await createEncounter({
        patient_id: Number(patientNumber),
        age,
        time_in_hospital: Number(timeInHospital),
        number_inpatient: Number(inpatientVisits),
        number_emergency: Number(emergencyVisits),
        num_medications: Number(medications),
      });

      const saved = await getEncounter(encounter_id);
      setCreated(saved);
      setEncounters((prev) => [...prev, saved]);
      resetForm();
    } catch (err) {
      setError(`Could not add encounter: ${(err as Error).message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <div className="encounter-card">
        <div className="card-header">Diabetes Patient Management</div>

        <form onSubmit={addEncounter}>
          <h3>Add Patient Encounter</h3>

          <div className="form-group">
            <label htmlFor="patientNumber">Patient Number</label>
            <input
              id="patientNumber"
              type="number"
              min="1"
              value={patientNumber}
              onChange={(e) => setPatientNumber(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="age">Age</label>
            <select
              id="age"
              className="age-select"
              value={age}
              onChange={(e) => setAge(e.target.value)}
            >
              <option value="">Age Group</option>
              {AGE_GROUPS.map((group) => (
                <option key={group} value={group}>
                  {group}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="timeInHospital">Time in Hospital (days)</label>
            <input
              id="timeInHospital"
              type="number"
              min="0"
              value={timeInHospital}
              onChange={(e) => setTimeInHospital(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="inpatientVisits">Inpatient Visits</label>
            <input
              id="inpatientVisits"
              type="number"
              min="0"
              value={inpatientVisits}
              onChange={(e) => setInpatientVisits(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="emergencyVisits">Emergency Visits</label>
            <input
              id="emergencyVisits"
              type="number"
              min="0"
              value={emergencyVisits}
              onChange={(e) => setEmergencyVisits(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="medications">Medications</label>
            <input
              id="medications"
              type="number"
              min="0"
              value={medications}
              onChange={(e) => setMedications(e.target.value)}
            />
          </div>

          {error && <p className="error">{error}</p>}
          {created && (
            <p className="success">
              Encounter {created.encounter_id} saved for patient {created.patient_id}.
            </p>
          )}

          <div className="button-container">
            <button type="submit" disabled={submitting}>
              Add <span className="arrow">&gt;</span>
            </button>
          </div>
        </form>
      </div>

      <div className="table-card">
        <div className="card-header">Encounters</div>
        <table className="encounter-table">
          <thead>
            <tr>
              <th>Encounter ID</th>
              <th>Patient ID</th>
              <th>Age</th>
              <th>Days in Hospital</th>
              <th>Inpatient</th>
              <th>Emergency</th>
              <th>Medications</th>
              <th>Risk Score</th>
              <th>Risk Level</th>
            </tr>
          </thead>
          <tbody>
            {encounters.map((enc) => (
              <tr
                key={enc.encounter_id}
                className={enc.encounter_id === created?.encounter_id ? "new-row" : undefined}
              >
                <td>{enc.encounter_id}</td>
                <td>{enc.patient_id}</td>
                <td>{enc.age}</td>
                <td>{enc.time_in_hospital}</td>
                <td>{enc.number_inpatient}</td>
                <td>{enc.number_emergency}</td>
                <td>{enc.num_medications}</td>
                <td>{enc.risk_score ?? "—"}</td>
                <td>{enc.risk_level ?? "Pending"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default EncounterDetails;
