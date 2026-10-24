
import { useState } from "react";
import "./EncounterDetails.css";

interface Encounter {
  patientNumber: string;
  ageGroup: string;
  timeInHospital: number;
  inpatientVisits: number;
  emergencyVisits: number;
  medications: number;
}

function EncounterDetails() {
  const [encounter, setEncounter] = useState<Encounter>({
    patientNumber: "",
    ageGroup: "",
    timeInHospital: 0,
    inpatientVisits: 0,
    emergencyVisits: 0,
    medications: 0,
  });

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = event.target;

    setEncounter((previous) => ({
      ...previous,
      [name]:
        name === "patientNumber" || name === "ageGroup"
          ? value
          : Number(value),
    }));
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    console.log("Patient Encounter Details:", encounter);
    alert("Patient encounter added successfully!");
  };

  return (
    <div className="page">
      <div className="encounter-card">
        <header className="card-header">
          Diabetes Patient Management
        </header>

        <form onSubmit={handleSubmit}>
          <h3>Add Patient Encounter</h3>

          <div className="form-group">
            <label htmlFor="patientNumber">Patient Number</label>
            <input
              id="patientNumber"
              name="patientNumber"
              type="text"
              value={encounter.patientNumber}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="ageGroup">Age</label>
            <select
              id="ageGroup"
              name="ageGroup"
              value={encounter.ageGroup}
              onChange={handleChange}
              required
            >
              <option value="">Age Group</option>
              <option value="0-18">0–18 years</option>
              <option value="19-40">19–40 years</option>
              <option value="41-60">41–60 years</option>
              <option value="60+">Above 60 years</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="timeInHospital">
              Time in Hospital (days)
            </label>
            <input
              id="timeInHospital"
              name="timeInHospital"
              type="number"
              min="0"
              value={encounter.timeInHospital}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="inpatientVisits">Inpatient Visits</label>
            <input
              id="inpatientVisits"
              name="inpatientVisits"
              type="number"
              min="0"
              value={encounter.inpatientVisits}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="emergencyVisits">Emergency Visits</label>
            <input
              id="emergencyVisits"
              name="emergencyVisits"
              type="number"
              min="0"
              value={encounter.emergencyVisits}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="medications">Medications</label>
            <input
              id="medications"
              name="medications"
              type="number"
              min="0"
              value={encounter.medications}
              onChange={handleChange}
              required
            />
          </div>

          <div className="button-container">
            <button type="submit">
              Add <span className="arrow">❯</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EncounterDetails;
