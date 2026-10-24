import { useState } from "react";
import HighCarePatients from "./HighCarePatients";
import PatientSearch from "./PatientSearch";
import StatusTracking from "./StatusTracking";
import "./App.css";

type Tab = "search" | "high-care";

function App() {
  const [tab, setTab] = useState<Tab>("search");
  // When set, the status tracking screen is shown for this encounter
  const [selectedEncounter, setSelectedEncounter] = useState<number | null>(null);

  const openTab = (next: Tab) => {
    setTab(next);
    setSelectedEncounter(null);
  };

  return (
    <div className="page">
      <nav className="tabs">
        <button className={tab === "search" && !selectedEncounter ? "active" : ""} onClick={() => openTab("search")}>
          Search Patient
        </button>
        <button
          className={tab === "high-care" && !selectedEncounter ? "active" : ""}
          onClick={() => openTab("high-care")}
        >
          High Care Patients
        </button>
      </nav>

      {selectedEncounter !== null && (
        <StatusTracking encounterId={selectedEncounter} onBack={() => setSelectedEncounter(null)} />
      )}

      {/* Search stays mounted (just hidden) so its filters and results survive a trip to the status screen */}
      <div hidden={selectedEncounter !== null || tab !== "search"}>
        <PatientSearch onSelectEncounter={setSelectedEncounter} />
      </div>
      {selectedEncounter === null && tab === "high-care" && (
        <HighCarePatients onSelectEncounter={setSelectedEncounter} />
      )}
    </div>
  );
}

export default App;
