"""Business logic: validation, then delegate storage to the repository."""

import repository
from models import (
    Encounter,
    HighCarePatient,
    InterventionUpdate,
    InterventionUpdateCreate,
    PatientSearch,
)


class EncounterNotFound(Exception):
    pass


def init_db() -> None:
    repository.init_db()


def get_encounter(encounter_id: int) -> Encounter | None:
    return repository.find_encounter(encounter_id)


def search_patients(filters: PatientSearch) -> list[Encounter]:
    """Search by patient id and/or minimum risk score and/or risk level."""
    return repository.search_encounters(filters)


def list_high_care_patients() -> list[HighCarePatient]:
    return repository.find_high_care_patients()


def get_intervention_history(encounter_id: int) -> list[InterventionUpdate]:
    if repository.find_encounter(encounter_id) is None:
        raise EncounterNotFound(encounter_id)
    return repository.find_intervention_updates(encounter_id)


def update_intervention_status(encounter_id: int, data: InterventionUpdateCreate) -> InterventionUpdate:
    """Record a new status for the encounter; history is kept, never overwritten."""
    if repository.find_encounter(encounter_id) is None:
        raise EncounterNotFound(encounter_id)

    data = data.model_copy(update={"assigned_to": data.assigned_to.strip(), "notes": data.notes.strip()})
    if data.status in ("In Progress", "Completed") and not data.assigned_to:
        raise ValueError(f"Assigned To is required when status is '{data.status}'")

    return repository.insert_intervention_update(encounter_id, data)
