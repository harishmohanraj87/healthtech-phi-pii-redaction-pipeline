"""
benchmark.py
Yash Kulkarni - Detection Engine Lead
Week 3 / Day 6: Accuracy + performance benchmarking on large clinical notes.

Per the team roadmap, Week 3 goals for the Detection Engine are:
  - Accuracy
  - Benchmarking
  - Edge cases
  - Large clinical notes

This script builds a realistic multi-paragraph clinical note (the kind
a real EHR export might contain), runs it through the regex detector,
and reports:
  1. Detection speed (how long it takes to scan the text)
  2. Throughput (characters processed per second)
  3. A breakdown of how many entities of each type were found
  4. A manual accuracy check against known "ground truth" entities
     planted in the sample text

Run with: python3 detectors/benchmark.py
"""

import time
from collections import Counter

from detectors.regex_detector import detect


# ---------------------------------------------------------------------------
# A large, realistic multi-paragraph clinical note. Repeated and varied
# to simulate a longer EHR document (~5x a typical single-visit note).
# ---------------------------------------------------------------------------

def _build_large_clinical_note() -> str:
    base_note = """
Patient: John Doe, 65 years old, MRN: 1029384756, SSN 123-45-6789.
Residing at 742 Evergreen Terrace, zip code 60614.
Contacted on 04/12/2025 via email john.doe@example.com or phone (555) 123-4567.
Chief complaint: Patient reports increasing tremors and rigidity over the past
6 months, consistent with a diagnosis of Parkinson Disease. Family history
notable for Alzheimer's disease in mother.
Vitals: Blood pressure 120/80, heart rate 72 bpm, temperature 98.6F.
Accessed patient record from IP 192.168.1.10 for chart review.
Follow-up appointment scheduled for January 5, 2026.
Referred to Dr. Sarah Chen, Neurology, at Mercy General Hospital.
Insurance verification completed. Patient also has history of Crohn's disease,
managed with current medication regimen. No history of Down Syndrome or
other congenital conditions in the patient's own record.
"""
    # Simulate a longer document by repeating with slight variation
    # (different MRNs/dates/names per "visit" section)
    sections = []
    for i in range(20):
        section = base_note.replace("1029384756", str(1000000000 + i))
        section = section.replace("123-45-6789", f"{100+i:03d}-45-6789")
        sections.append(f"\n--- Visit Note {i+1} ---\n{section}")
    return "\n".join(sections)


def run_benchmark():
    text = _build_large_clinical_note()
    char_count = len(text)

    print(f"Benchmark input: {char_count:,} characters "
          f"(~{char_count / 1000:.1f} KB, {text.count('Visit Note')} visit sections)\n")

    # --- Performance ---
    start = time.perf_counter()
    detections = detect(text)
    elapsed = time.perf_counter() - start

    throughput = char_count / elapsed if elapsed > 0 else float("inf")

    print("=== Performance ===")
    print(f"Time taken:  {elapsed*1000:.2f} ms")
    print(f"Throughput:  {throughput:,.0f} characters/second")
    print(f"Total detections: {len(detections)}")

    # --- Breakdown by entity type ---
    counts = Counter(d.entity_type for d in detections)
    print("\n=== Entity Breakdown ===")
    for entity_type, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {entity_type:12s} {count}")

    # --- Accuracy check: known false-positive risks ---
    print("\n=== Accuracy Checks ===")
    redacted = text
    for d in sorted(detections, key=lambda x: x.start, reverse=True):
        redacted = redacted[:d.start] + f"[{d.entity_type}]" + redacted[d.end:]

    checks = [
        ("Parkinson Disease NOT redacted", "Parkinson Disease" in redacted),
        ("Alzheimer's disease NOT redacted", "Alzheimer's disease" in redacted),
        ("Crohn's disease NOT redacted", "Crohn's disease" in redacted),
        ("Down Syndrome NOT redacted", "Down Syndrome" in redacted),
        ("Blood pressure 120/80 NOT redacted", "120/80" in redacted),
        ("MRN values ARE redacted", "1000000000" not in redacted),
        ("Email addresses ARE redacted", "john.doe@example.com" not in redacted),
        ("Phone numbers ARE redacted", "(555) 123-4567" not in redacted),
    ]

    all_passed = True
    for label, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status}] {label}")

    print(f"\nOverall: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED'}")
    return all_passed


if __name__ == "__main__":
    run_benchmark()
