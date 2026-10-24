"""Business logic for encounters: validation, then delegate storage to the repository."""

import repository
from models import AGE_GROUPS, Encounter, EncounterCreate, PatientSearch


def init_db() -> None:
    repository.init_db()


def create_encounter(data: EncounterCreate) -> Encounter:
    """Validate and insert a new encounter, returning the stored row."""
    if data.age not in AGE_GROUPS:
        raise ValueError(f"Invalid age group: {data.age}")

    new_id = repository.insert_encounter(data)
    encounter = repository.find_encounter(new_id)
    assert encounter is not None
    return encounter


def get_encounter(encounter_id: int) -> Encounter | None:
    return repository.find_encounter(encounter_id)


def list_encounters() -> list[Encounter]:
    return repository.find_all_encounters()


def search_patients(filters: PatientSearch) -> list[Encounter]:
    """Search by patient id and/or minimum risk score and/or risk level."""
    return repository.search_encounters(filters)
