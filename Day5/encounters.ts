import { Encounter } from "./Encounter";

const encounters: Encounter[] = [
  {
    encounter_id: 101,
    patient_id: 1001,
    risk_score: 25,
    risk_level: "Low",
  },
  {
    encounter_id: 102,
    patient_id: 1002,
    risk_score: 65,
    risk_level: "Medium",
  },
  {
    encounter_id: 103,
    patient_id: 1003,
    risk_score: 90,
    risk_level: "High",
  },
];

console.log(encounters);