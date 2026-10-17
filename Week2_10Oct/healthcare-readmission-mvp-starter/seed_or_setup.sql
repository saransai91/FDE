-- Run schema.sql first. This file contains optional verification queries.
-- Do not insert invented patient records into the real assignment dataset.

SELECT COUNT(*) AS total_encounters FROM patient_encounters;

SELECT risk_level, COUNT(*) AS encounter_count
FROM patient_encounters
GROUP BY risk_level
ORDER BY risk_level;

SELECT status, COUNT(*) AS intervention_count
FROM care_interventions
GROUP BY status
ORDER BY status;
