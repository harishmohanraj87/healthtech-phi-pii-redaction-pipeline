"""
test_combined_detector.py
Yash Kulkarni - Detection Engine Lead
Week 2 / Day 5: Tests for the combined regex + NLP detection layer.

NOTE: These tests exercise the combined detector in "regex-only mode"
since Presidio may not be installed in every environment. The
CombinedDetector class is designed to degrade gracefully when Presidio
isn't available, which is exactly what's being tested here. Once
Presidio is installed locally, the NLP layer activates automatically
without any code changes.

Run with: pytest tests/test_combined_detector.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.combined_detector import CombinedDetector


def test_regex_layer_still_works_without_presidio():
    detector = CombinedDetector()
    text = "Patient MRN: 1029384756 contacted on 04/12/2025."
    detections = detector.detect(text)
    types = {d.entity_type for d in detections}
    assert "MRN" in types
    assert "DATE" in types


def test_all_detections_come_from_regex_when_presidio_unavailable():
    detector = CombinedDetector()
    text = "Email john.doe@example.com or call (555) 123-4567."
    detections = detector.detect(text)
    assert len(detections) > 0
    for d in detections:
        assert d.source == "regex"


def test_parkinson_disease_not_redacted():
    detector = CombinedDetector()
    text = "Patient was diagnosed with Parkinson Disease last year."
    redacted = detector.redact(text)
    assert "Parkinson Disease" in redacted


def test_combined_redact_full_note():
    detector = CombinedDetector()
    text = (
        "Patient John Doe, MRN: 1029384756, SSN 123-45-6789, "
        "contacted on 04/12/2025 via email john.doe@example.com "
        "or phone (555) 123-4567."
    )
    redacted = detector.redact(text)
    assert "1029384756" not in redacted
    assert "123-45-6789" not in redacted
    assert "john.doe@example.com" not in redacted
    assert "(555) 123-4567" not in redacted


def test_no_duplicate_or_overlapping_spans():
    detector = CombinedDetector()
    text = (
        "Patient John Doe, 65 years old, MRN: 1029384756, "
        "SSN 123-45-6789, contacted on 04/12/2025."
    )
    detections = detector.detect(text)
    spans = [(d.start, d.end) for d in detections]

    # No exact duplicates
    assert len(spans) == len(set(spans))

    # No overlapping spans at all
    sorted_spans = sorted(spans)
    for i in range(len(sorted_spans) - 1):
        assert sorted_spans[i][1] <= sorted_spans[i + 1][0], (
            f"Overlap found between {sorted_spans[i]} and {sorted_spans[i + 1]}"
        )


def test_empty_text_returns_empty_list():
    detector = CombinedDetector()
    assert detector.detect("") == []


def test_text_with_no_entities_returns_empty_list():
    detector = CombinedDetector()
    text = "The weather was nice today and the patient felt better."
    detections = detector.detect(text)
    assert detections == []
