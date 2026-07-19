"""
test_edge_cases.py
Yash Kulkarni - Detection Engine Lead
Week 3 / Day 6: Edge case tests for large, realistic clinical notes.

These go beyond the unit-level tests in test_regex_detector.py and
test real-world clinical documentation patterns that could trip up
the detection engine: multi-visit documents, mixed formatting,
abbreviations, and dense entity clustering.

Run with: pytest tests/test_edge_cases.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.regex_detector import detect, redact
from detectors.combined_detector import CombinedDetector


# ---------------------------------------------------------------------------
# Large document handling
# ---------------------------------------------------------------------------

def test_handles_large_document_without_error():
    # Simulate a large multi-page note (~10,000 chars)
    section = (
        "Patient MRN: 1029384756 contacted on 04/12/2025 via "
        "john.doe@example.com. Diagnosed with Parkinson Disease. "
    )
    large_text = section * 100  # ~10,900 characters
    detections = detect(large_text)
    assert len(detections) > 0
    # Every MRN in the repeated text should be found
    mrn_count = sum(1 for d in detections if d.entity_type == "MRN")
    assert mrn_count == 100


def test_large_document_performance_reasonable():
    import time
    section = "Patient contacted on 04/12/2025 at (555) 123-4567. "
    large_text = section * 500  # ~26,000 characters
    start = time.perf_counter()
    detect(large_text)
    elapsed = time.perf_counter() - start
    # Should process well under a second even for a large note
    assert elapsed < 2.0


# ---------------------------------------------------------------------------
# Dense entity clustering (multiple entities back-to-back, minimal spacing)
# ---------------------------------------------------------------------------

def test_densely_packed_entities():
    text = "MRN:1029384756,SSN:123-45-6789,DOB:04/12/1960,Phone:5551234567"
    detections = detect(text)
    types = {d.entity_type for d in detections}
    # At minimum MRN and SSN should be found even with no spacing
    assert "MRN" in types
    assert "SSN" in types


def test_multiple_dates_in_one_sentence():
    text = "Admitted 04/12/2025, discharged 04/15/2025, follow-up 05/01/2025."
    detections = detect(text)
    dates = [d for d in detections if d.entity_type == "DATE"]
    assert len(dates) == 3


# ---------------------------------------------------------------------------
# Multi-visit document structure (repeated headers/sections)
# ---------------------------------------------------------------------------

def test_multi_visit_document_all_mrns_unique():
    text = "\n".join(
        f"--- Visit {i} --- MRN: {1000000000 + i}, seen on 04/{i+1:02d}/2025."
        for i in range(1, 6)
    )
    detections = detect(text)
    mrn_texts = {d.text for d in detections if d.entity_type == "MRN"}
    assert len(mrn_texts) == 5  # all 5 MRNs distinct and detected


# ---------------------------------------------------------------------------
# Medical terminology density (lots of disease names near real PHI)
# ---------------------------------------------------------------------------

def test_multiple_disease_names_near_real_phi_not_confused():
    text = (
        "Patient history includes Parkinson Disease, Alzheimer's disease, "
        "Crohn's disease, and Down Syndrome. MRN: 1029384756 on file. "
        "Contact: patient@example.com."
    )
    redacted = redact(text)
    # All 4 disease names should survive redaction
    for disease in ["Parkinson Disease", "Alzheimer's disease",
                     "Crohn's disease", "Down Syndrome"]:
        assert disease in redacted
    # Real PHI should still be redacted
    assert "1029384756" not in redacted
    assert "patient@example.com" not in redacted


# ---------------------------------------------------------------------------
# Combined detector on a full realistic note
# ---------------------------------------------------------------------------

def test_combined_detector_on_realistic_note():
    detector = CombinedDetector()
    text = (
        "Patient John Doe, 65 years old, MRN: 1029384756, SSN 123-45-6789, "
        "residing at 742 Evergreen Terrace, zip code 60614, diagnosed with "
        "Parkinson Disease. Blood pressure 120/80. Contacted on 04/12/2025 "
        "via john.doe@example.com or (555) 123-4567. Accessed from IP "
        "192.168.1.10."
    )
    redacted = detector.redact(text)

    # Structured PHI redacted
    assert "1029384756" not in redacted
    assert "123-45-6789" not in redacted
    assert "742 Evergreen Terrace" not in redacted
    assert "60614" not in redacted
    assert "john.doe@example.com" not in redacted
    assert "(555) 123-4567" not in redacted
    assert "192.168.1.10" not in redacted

    # Non-PHI preserved
    assert "Parkinson Disease" in redacted
    assert "120/80" in redacted
