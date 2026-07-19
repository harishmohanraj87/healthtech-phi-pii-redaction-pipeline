"""
accuracy_eval.py
Yash Kulkarni - Detection Engine Lead
Week 3 / Day 7: Precision / Recall / F1 measurement against a labeled
ground-truth dataset.

Why this exists:
  benchmark.py (Day 6) checks a handful of pass/fail assertions.
  This script goes further: it defines a labeled dataset of clinical
  note snippets where every PHI/PII entity AND every "trap" (medical
  terms, vitals, room numbers that should NOT be flagged) is known in
  advance. It then computes standard accuracy metrics:

    Precision = correct detections / all detections made
              (how many of our flags were actually right)
    Recall    = correct detections / all entities that should be found
              (how many real PHI entities did we actually catch)
    F1        = harmonic mean of precision and recall
              (single number balancing both)

  This is the kind of metric a mentor or reviewer will actually want
  to see, rather than just "the tests pass."

Run with: python3 detectors/accuracy_eval.py
"""

from dataclasses import dataclass
from typing import List, Tuple

from detectors.regex_detector import detect


@dataclass
class LabeledCase:
    """One test case: input text + the entities that SHOULD be found."""
    name: str
    text: str
    # List of (entity_type, exact_text) pairs that MUST be detected
    expected: List[Tuple[str, str]]
    # List of substrings that must NOT appear in any detection's text
    # (traps: medical terms, vitals, room numbers, etc.)
    must_not_flag: List[str]


# ---------------------------------------------------------------------------
# Labeled dataset — 15 realistic clinical note snippets covering all
# 9 entity types plus known false-positive traps.
# ---------------------------------------------------------------------------

DATASET: List[LabeledCase] = [
    LabeledCase(
        "basic_contact_info",
        "Contact patient at (555) 123-4567 or john.doe@example.com.",
        expected=[("PHONE", "(555) 123-4567"), ("EMAIL", "john.doe@example.com")],
        must_not_flag=[],
    ),
    LabeledCase(
        "mrn_and_ssn",
        "MRN: 1029384756, SSN 123-45-6789 on file.",
        expected=[("MRN", "MRN: 1029384756"), ("SSN", "123-45-6789")],
        must_not_flag=[],
    ),
    LabeledCase(
        "date_formats",
        "Admitted 04/12/2025, discharged on January 5, 2026.",
        expected=[("DATE", "04/12/2025"), ("DATE", "January 5, 2026")],
        must_not_flag=[],
    ),
    LabeledCase(
        "address_and_zip",
        "Lives at 742 Evergreen Terrace, zip code 60614.",
        expected=[("ADDRESS", "742 Evergreen Terrace"), ("ZIP", "60614")],
        must_not_flag=[],
    ),
    LabeledCase(
        "age_and_ip",
        "This 65-year-old patient's record was accessed from IP 192.168.1.10.",
        expected=[("AGE", "65-year-old"), ("IP_ADDRESS", "192.168.1.10")],
        must_not_flag=[],
    ),
    LabeledCase(
        "blood_pressure_trap",
        "Blood pressure 120/80 recorded, patient stable.",
        expected=[],
        must_not_flag=["120/80"],
    ),
    LabeledCase(
        "room_number_trap",
        "Patient in room 60614, bed 3.",
        expected=[],
        must_not_flag=["60614"],  # should NOT be caught as ZIP without context
    ),
    LabeledCase(
        "parkinson_disease_trap",
        "Diagnosed with Parkinson Disease last year.",
        expected=[],
        must_not_flag=["Parkinson Disease"],
    ),
    LabeledCase(
        "alzheimers_trap",
        "Family history of Alzheimer's disease noted.",
        expected=[],
        must_not_flag=["Alzheimer's disease"],
    ),
    LabeledCase(
        "vitals_no_date_confusion",
        "Temperature 98.6F, heart rate 72 bpm, O2 sat 98%.",
        expected=[],
        must_not_flag=[],
    ),
    LabeledCase(
        "multiple_entities_dense",
        "MRN:1029384756,SSN:123-45-6789,Phone:5551234567",
        expected=[("MRN", "MRN:1029384756"), ("SSN", "123-45-6789")],
        must_not_flag=[],
    ),
    LabeledCase(
        "email_with_subdomain",
        "Records sent to patient.records@clinic.hospital.org.",
        expected=[("EMAIL", "patient.records@clinic.hospital.org")],
        must_not_flag=[],
    ),
    LabeledCase(
        "age_label_format",
        "Age: 42, presenting with fever.",
        expected=[("AGE", "Age: 42")],
        must_not_flag=[],
    ),
    LabeledCase(
        "full_clinical_note",
        "Patient John Doe, 65 years old, MRN: 1029384756, residing at "
        "742 Evergreen Terrace, diagnosed with Crohn's disease. Blood "
        "pressure 120/80. Contacted 04/12/2025 via john.doe@example.com.",
        expected=[
            ("AGE", "65 years old"),
            ("MRN", "MRN: 1029384756"),
            ("ADDRESS", "742 Evergreen Terrace"),
            ("DATE", "04/12/2025"),
            ("EMAIL", "john.doe@example.com"),
        ],
        must_not_flag=["Crohn's disease", "120/80"],
    ),
    LabeledCase(
        "no_entities_plain_text",
        "The patient reported feeling better after the treatment plan.",
        expected=[],
        must_not_flag=[],
    ),
    LabeledCase(
        "turner_syndrome_trap",
        "Patient has a history of Turner syndrome since childhood.",
        expected=[],
        must_not_flag=["Turner syndrome"],
    ),
    LabeledCase(
        "marfan_trap",
        "Cardiology consult ordered given known Marfan syndrome.",
        expected=[],
        must_not_flag=["Marfan syndrome"],
    ),
    LabeledCase(
        "guillain_barre_trap",
        "Recovering well after an episode of Guillain-Barre syndrome.",
        expected=[],
        must_not_flag=["Guillain-Barre syndrome"],
    ),
]


def evaluate() -> dict:
    total_expected = 0
    total_detected = 0
    true_positives = 0
    false_positives = 0
    trap_violations = []

    for case in DATASET:
        detections = detect(case.text)
        detected_pairs = {(d.entity_type, d.text) for d in detections}
        expected_pairs = set(case.expected)

        total_expected += len(expected_pairs)
        total_detected += len(detected_pairs)
        true_positives += len(detected_pairs & expected_pairs)
        false_positives += len(detected_pairs - expected_pairs)

        # Check traps: none of the "must not flag" substrings should
        # appear in any detected entity's text
        for trap in case.must_not_flag:
            for d in detections:
                if trap in d.text or d.text in trap:
                    trap_violations.append((case.name, trap, d.entity_type, d.text))

    false_negatives = total_expected - true_positives

    precision = true_positives / total_detected if total_detected else 1.0
    recall = true_positives / total_expected if total_expected else 1.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "total_cases": len(DATASET),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "trap_violations": trap_violations,
    }


def print_report():
    results = evaluate()

    print("=== Accuracy Evaluation ===")
    print(f"Dataset size:      {results['total_cases']} labeled cases")
    print(f"True positives:    {results['true_positives']}")
    print(f"False positives:   {results['false_positives']}")
    print(f"False negatives:   {results['false_negatives']}")
    print()
    print(f"Precision: {results['precision']*100:.1f}%")
    print(f"Recall:    {results['recall']*100:.1f}%")
    print(f"F1 Score:  {results['f1']*100:.1f}%")
    print()

    if results["trap_violations"]:
        print("=== TRAP VIOLATIONS (false positives on protected terms) ===")
        for case_name, trap, entity_type, text in results["trap_violations"]:
            print(f"  [{case_name}] '{trap}' was flagged as {entity_type} ('{text}')")
    else:
        print("No trap violations — all protected terms correctly ignored.")

    return results


if __name__ == "__main__":
    print_report()
