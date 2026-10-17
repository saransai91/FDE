import repository

def calculate_risk(encounter: dict) -> tuple[int, str]:
    """Explainable assignment rule. Never use the readmitted outcome here."""
    score = 0
    if int(encounter["number_inpatient"]) >= 3:
        score += 3
    if int(encounter["number_emergency"]) >= 2:
        score += 2
    if int(encounter["number_outpatient"]) >= 3:
        score += 1
    if int(encounter["time_in_hospital"]) >= 7:
        score += 1
    if int(encounter["num_medications"]) >= 20:
        score += 1

    if score >= 5:
        level = "HIGH"
    elif score >= 3:
        level = "MEDIUM"
    else:
        level = "LOW"
    return score, level

def list_encounters(limit: int, offset: int):
    return repository.list_encounters(limit, offset)

def get_encounter(encounter_id: int):
    return repository.get_encounter(encounter_id)

def get_care_queue(limit: int, offset: int):
    return repository.get_care_queue(limit, offset)

def get_high_risk_queue(limit: int, offset: int):
    return repository.get_care_queue(limit, offset, high_only=True)

def update_intervention(encounter_id: int, fields: dict):
    result = repository.update_intervention(encounter_id, fields)
    if result is None:
        raise ValueError(f"Encounter {encounter_id} was not found")
    return result

def operations_summary():
    return repository.operations_summary()

def readmission_analysis():
    return repository.readmission_analysis()

def management_dashboard():
    return repository.management_dashboard()
