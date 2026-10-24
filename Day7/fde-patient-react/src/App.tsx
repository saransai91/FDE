import { useState } from "react";
import Header from "./components/Header";
import PatientTable from "./components/PatientTable";
import Pagination from "./components/Pagination";
import EncounterForm from "./components/EncounterForm";
import useEncounters from "./hooks/useEncounters";
import "./App.css";

const PAGE_SIZE = 5;

function App() {
  const { encounters, loading, error, createEncounter, deleteEncounter } =
    useEncounters();
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(encounters.length / PAGE_SIZE));
  // Deleting the last row on the last page would leave us past the end
  const page = Math.min(currentPage, totalPages);
  const pageEncounters = encounters.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE,
  );

  const handleDelete = (encounterId: number) => {
    if (window.confirm(`Delete encounter ${encounterId}?`)) {
      deleteEncounter(encounterId);
    }
  };

  return (
    <div className="app">
      <Header title="Patient Encounters" count={encounters.length} />
      <EncounterForm onCreate={createEncounter} />
      {error && <p className="error">Error: {error}</p>}
      {loading ? (
        <p>Loading encounters...</p>
      ) : (
        <>
          <PatientTable encounters={pageEncounters} onDelete={handleDelete} />
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </>
      )}
    </div>
  );
}

export default App;
