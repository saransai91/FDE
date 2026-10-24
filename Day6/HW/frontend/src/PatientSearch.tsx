import { useState } from "react";
import { searchPatients } from "./api";
import { RISK_LEVELS, type Encounter, type PatientSearch as Filters, type RiskLevel } from "./types";

interface Props {
  onSelectEncounter: (encounterId: number) => void;
}

function PatientSearch({ onSelectEncounter }: Props) {
  const [patientNumber, setPatientNumber] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [riskScore, setRiskScore] = useState("");

  const [results, setResults] = useState<Encounter[] | null>(null);
  const [error, setError] = useState("");
  const [searching, setSearching] = useState(false);

  // Empty fields are left out, so the API only filters on what was entered
  const search = async (e: React.FormEvent) => {
    e.preventDefault();
    const filters: Filters = {};
    if (patientNumber) filters.patient_id = Number(patientNumber);
    if (riskLevel) filters.risk_level = riskLevel as RiskLevel;
    if (riskScore) filters.min_risk_score = Number(riskScore);

    setSearching(true);
    setError("");
    try {
      setResults(await searchPatients(filters));
    } catch (err) {
      setResults(null);
      setError(`Search failed: ${(err as Error).message}`);
    } finally {
      setSearching(false);
    }
  };

  return (
    <>
      <div className="card">
        <div className="card-header">Diabetes Patient Management</div>

        <form onSubmit={search}>
          <h3>Search Patient</h3>

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
            <label htmlFor="riskLevel">Risk Level</label>
            <select
              id="riskLevel"
              className="short-select"
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value)}
            >
              <option value="">Any</option>
              {RISK_LEVELS.map((level) => (
                <option key={level} value={level}>
                  {level}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="riskScore">Min Risk Score (0–100)</label>
            <input
              id="riskScore"
              type="number"
              min="0"
              max="100"
              step="any"
              value={riskScore}
              onChange={(e) => setRiskScore(e.target.value)}
            />
          </div>

          {error && <p className="error">{error}</p>}

          <div className="button-container">
            <button type="submit" disabled={searching}>
              Search <span className="arrow">&gt;</span>
            </button>
          </div>
        </form>
      </div>

      {results && (
        <div className="table-card">
          {results.length === 0 ? (
            <p className="empty">No patients match these filters.</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Encounter Id</th>
                  <th>Patient Number</th>
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
                {results.map((enc) => (
                  <tr key={enc.encounter_id}>
                    <td>
                      <button className="link" onClick={() => onSelectEncounter(enc.encounter_id)}>
                        {enc.encounter_id}
                      </button>
                    </td>
                    <td>{enc.patient_id}</td>
                    <td>{enc.age}</td>
                    <td>{enc.time_in_hospital}</td>
                    <td>{enc.number_inpatient}</td>
                    <td>{enc.number_emergency}</td>
                    <td>{enc.num_medications}</td>
                    <td>{enc.risk_score ?? "—"}</td>
                    <td>
                      {enc.risk_level ? (
                        <span className={`badge risk-${enc.risk_level.toLowerCase()}`}>{enc.risk_level}</span>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  );
}

export default PatientSearch;
