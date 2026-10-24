import { useEffect, useState } from "react";
import { getEncounter, getInterventionHistory, updateInterventionStatus } from "./api";
import { formatDate, statusClass } from "./HighCarePatients";
import { INTERVENTION_STATUSES, type Encounter, type InterventionStatus, type InterventionUpdate } from "./types";

interface Props {
  encounterId: number;
  onBack: () => void;
}

function StatusTracking({ encounterId, onBack }: Props) {
  const [encounter, setEncounter] = useState<Encounter | null>(null);
  const [history, setHistory] = useState<InterventionUpdate[]>([]);

  const [status, setStatus] = useState<InterventionStatus>("Not Started");
  const [assignedTo, setAssignedTo] = useState("");
  const [notes, setNotes] = useState("");

  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  // Load the encounter and its history; pre-fill the form with the latest status
  useEffect(() => {
    Promise.all([getEncounter(encounterId), getInterventionHistory(encounterId)])
      .then(([enc, updates]) => {
        setEncounter(enc);
        setHistory(updates);
        if (updates.length > 0) {
          setStatus(updates[0].status);
          setAssignedTo(updates[0].assigned_to);
        }
      })
      .catch((err) => setError(`Could not load encounter ${encounterId}: ${err.message}`));
  }, [encounterId]);

  const update = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSaved(false);
    try {
      const created = await updateInterventionStatus(encounterId, { status, assigned_to: assignedTo, notes });
      setHistory((prev) => [created, ...prev]);
      setNotes("");
      setSaved(true);
    } catch (err) {
      setError(`Could not update status: ${(err as Error).message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card status-card">
      <div className="card-header">Diabetes Patient Management</div>

      <button className="link back" onClick={onBack}>
        &lt; Back
      </button>

      <form onSubmit={update} className="status-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="encounterId">Encounter Id</label>
            <input id="encounterId" value={encounterId} readOnly />
          </div>
          <div className="form-group">
            <label htmlFor="patientNumber">Patient Number</label>
            <input id="patientNumber" value={encounter?.patient_id ?? ""} readOnly />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="status">Status</label>
            <select id="status" value={status} onChange={(e) => setStatus(e.target.value as InterventionStatus)}>
              {INTERVENTION_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="assignedTo">Assigned To</label>
            <input
              id="assignedTo"
              maxLength={100}
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="notes">Notes</label>
          <textarea id="notes" maxLength={500} rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>

        {error && <p className="error">{error}</p>}
        {saved && <p className="success">Status updated.</p>}

        <div className="button-container">
          <button type="submit" disabled={saving || !encounter}>
            Update
          </button>
        </div>
      </form>

      <div className="history">
        {history.length === 0 ? (
          <p className="empty">No updates yet for this encounter.</p>
        ) : (
          <ul>
            {history.map((u) => (
              <li key={u.update_id}>
                <div className="history-head">
                  <span className={statusClass(u.status)}>{u.status}</span>
                  <span className="muted">{u.assigned_to || "Unassigned"}</span>
                  <span className="muted right">{formatDate(u.updated_at)}</span>
                </div>
                {u.notes && <p className="history-notes">{u.notes}</p>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default StatusTracking;
