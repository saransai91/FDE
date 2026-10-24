import { useState } from "react";
import type { FormEvent } from "react";
import { AGE_GROUPS } from "../types";
import type { EncounterCreate } from "../types";

interface EncounterFormProps {
  onCreate: (data: EncounterCreate) => Promise<boolean>;
}

const EMPTY_FORM: EncounterCreate = {
  patient_id: 0,
  age: AGE_GROUPS[5],
  time_in_hospital: 0,
  number_inpatient: 0,
  number_emergency: 0,
  num_medications: 0,
};

const NUMBER_FIELDS: { name: keyof EncounterCreate; label: string; min: number }[] = [
  { name: "patient_id", label: "Patient ID", min: 1 },
  { name: "time_in_hospital", label: "Days in Hospital", min: 0 },
  { name: "number_inpatient", label: "Inpatient Visits", min: 0 },
  { name: "number_emergency", label: "Emergency Visits", min: 0 },
  { name: "num_medications", label: "Medications", min: 0 },
];

function EncounterForm({ onCreate }: EncounterFormProps) {
  const [form, setForm] = useState<EncounterCreate>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    const ok = await onCreate(form);
    setSaving(false);
    if (ok) setForm(EMPTY_FORM);
  };

  return (
    <form className="encounter-form" onSubmit={handleSubmit}>
      {NUMBER_FIELDS.map(({ name, label, min }) => (
        <label key={name}>
          {label}
          <input
            type="number"
            min={min}
            required
            value={form[name]}
            onChange={(e) => setForm({ ...form, [name]: Number(e.target.value) })}
          />
        </label>
      ))}

      <label>
        Age
        <select
          value={form.age}
          onChange={(e) => setForm({ ...form, age: e.target.value })}
        >
          {AGE_GROUPS.map((group) => (
            <option key={group} value={group}>
              {group}
            </option>
          ))}
        </select>
      </label>

      <button type="submit" disabled={saving}>
        {saving ? "Adding..." : "Add Encounter"}
      </button>
    </form>
  );
}

export default EncounterForm;
