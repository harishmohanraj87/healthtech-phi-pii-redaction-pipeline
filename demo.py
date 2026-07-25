"""
demo.py
Yash Kulkarni - Detection Engine Lead
Week 3/4: Presentation demo for the PHI/PII Detection Engine.

Run this for a clean, screen-recording-friendly walkthrough of what the
detection engine does — good for the Week 4 demo video / mentor review.

Run with: python3 demo.py
"""

from detectors.combined_detector import CombinedDetector


SEPARATOR = "=" * 70


def print_header(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def run_demo():
    print_header("PHI/PII DETECTION ENGINE — LIVE DEMO")
    print("  Detection Engine Lead: Yash Kulkarni")
    print("  Regex layer: 9 entity types | NLP layer: Presidio + spaCy")

    detector = CombinedDetector()

    # ------------------------------------------------------------------
    # Demo 1: A realistic clinical note with multiple PHI types
    # ------------------------------------------------------------------
    print_header("DEMO 1: Realistic Clinical Note")

    note = (
        "Patient John Doe, 65 years old, MRN: 1029384756, SSN 123-45-6789, "
        "residing at 742 Evergreen Terrace, contacted on 04/12/2025 via "
        "email john.doe@example.com or phone (555) 123-4567."
    )

    print("\nOriginal note:")
    print(f"  {note}")

    detections = detector.detect(note)
    print(f"\nDetected {len(detections)} PHI/PII entities:")
    for d in detections:
        print(f"  [{d.entity_type:12s}] '{d.text}'  (source: {d.source})")

    print("\nRedacted output:")
    print(f"  {detector.redact(note)}")

    # ------------------------------------------------------------------
    # Demo 2: The critical "Parkinson Disease" requirement
    # ------------------------------------------------------------------
    print_header("DEMO 2: Medical Term Protection (Key Requirement)")

    medical_note = (
        "Patient was diagnosed with Parkinson Disease last year. "
        "Family history notable for Alzheimer's disease and Crohn's disease. "
        "Contact: patient@example.com."
    )

    print("\nOriginal note:")
    print(f"  {medical_note}")

    print("\nRedacted output:")
    redacted = detector.redact(medical_note)
    print(f"  {redacted}")

    print("\nVerification:")
    checks = [
        ("Parkinson Disease preserved", "Parkinson Disease" in redacted),
        ("Alzheimer's disease preserved", "Alzheimer's disease" in redacted),
        ("Crohn's disease preserved", "Crohn's disease" in redacted),
        ("Email correctly redacted", "patient@example.com" not in redacted),
    ]
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {label}")

    # ------------------------------------------------------------------
    # Demo 3: False-positive guards (things that should NOT be flagged)
    # ------------------------------------------------------------------
    print_header("DEMO 3: False-Positive Guards")

    vitals_note = "Blood pressure 120/80, patient in room 302, temperature 98.6F."
    print("\nOriginal note:")
    print(f"  {vitals_note}")

    detections = detector.detect(vitals_note)
    print(f"\nDetected {len(detections)} entities (expected: 0)")
    print("Redacted output (should be unchanged):")
    print(f"  {detector.redact(vitals_note)}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print_header("SUMMARY")
    print("""
  Entity types covered:
    Regex:  PHONE, EMAIL, DATE, MRN, SSN, ZIP, IP_ADDRESS, ADDRESS, AGE
    NLP:    PERSON, LOCATION, ORGANIZATION

  Accuracy (measured via accuracy_eval.py):
    Precision: 100.0%  |  Recall: 100.0%  |  F1: 100.0%

  Performance (measured via benchmark.py):
    ~1.8 million characters/second on realistic clinical documents

  Test coverage: 71 automated tests across regex, NLP, medical terms,
  combined detection, edge cases, and accuracy evaluation.
""")


if __name__ == "__main__":
    run_demo()
