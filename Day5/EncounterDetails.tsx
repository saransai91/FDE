import { useState } from "react";
import type { Encounter } from "./Encounter";

function EncounterDetails() {
  const [encounterId, setEncounterId] = useState("101");
  const [response, setResponse] = useState<Encounter | null>(null);

  const fetchEncounter = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/encounters/${encounterId}`
      );

      if (!res.ok) {
        throw new Error("Encounter not found");
      }

      const data: Encounter = await res.json();
      setResponse(data);

      console.log(JSON.stringify(data, null, 2));
    } catch (error) {
      setResponse(null);
      console.error(error);
    }
  };

  return (
    <div>
      <h2>Fetch Encounter</h2>

      <input
        type="number"
        value={encounterId}
        onChange={(e) => setEncounterId(e.target.value)}
      />

      <button onClick={fetchEncounter}>
        Fetch Encounter
      </button>

      {response && (
        <pre>{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}

export default EncounterDetails;import { useState } from "react";
import type { Encounter } from "./Encounter";

function EncounterDetails() {
  const [encounterId, setEncounterId] = useState("101");
  const [response, setResponse] = useState<Encounter | null>(null);

  const fetchEncounter = async () => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/encounters/${encounterId}`
      );

      if (!res.ok) {
        throw new Error("Encounter not found");
      }

      const data: Encounter = await res.json();
      setResponse(data);

      console.log(JSON.stringify(data, null, 2));
    } catch (error) {
      setResponse(null);
      console.error(error);
    }
  };

  return (
    <div>
      <h2>Fetch Encounter</h2>

      <input
        type="number"
        value={encounterId}
        onChange={(e) => setEncounterId(e.target.value)}
      />

      <button onClick={fetchEncounter}>
        Fetch Encounter
      </button>

      {response && (
        <pre>{JSON.stringify(response, null, 2)}</pre>
      )}
    </div>
  );
}

export default EncounterDetails;