"""
test_regex_detector.py
Yash Kulkarni - Detection Engine Lead
Week 1 / Day 3: Tests for ADDRESS, AGE + edge case hardening.

Run with: pytest tests/test_regex_detector.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.regex_detector import detect, redact


# ---------------------------------------------------------------------------
# ADDRESS tests
# ---------------------------------------------------------------------------

def test_address_basic_street():
    text = "Patient resides at 742 Evergreen Terrace."
    detections = detect(text)
    addrs = [d for d in detections if d.entity_type == "ADDRESS"]
    assert len(addrs) == 1
    assert addrs[0].text == "742 Evergreen Terrace"


def test_address_avenue():
    text = "Mailing address: 1600 Pennsylvania Ave"
    detections = detect(text)
    addrs = [d for d in detections if d.entity_type == "ADDRESS"]
    assert len(addrs) == 1


def test_address_multi_word_street_name():
    text = "Clinic located at 500 Martin Luther King Blvd"
    detections = detect(text)
    addrs = [d for d in detections if d.entity_type == "ADDRESS"]
    assert len(addrs) == 1


# ---------------------------------------------------------------------------
# AGE tests
# ---------------------------------------------------------------------------

def test_age_years_old_format():
    text = "Patient is 65 years old with a history of diabetes."
    detections = detect(text)
    ages = [d for d in detections if d.entity_type == "AGE"]
    assert len(ages) == 1


def test_age_hyphenated_format():
    text = "This 65-year-old male presented with chest pain."
    detections = detect(text)
    ages = [d for d in detections if d.entity_type == "AGE"]
    assert len(ages) == 1


def test_age_label_format():
    text = "Age: 42, presenting with mild fever."
    detections = detect(text)
    ages = [d for d in detections if d.entity_type == "AGE"]
    assert len(ages) == 1


# ---------------------------------------------------------------------------
# Edge case / false-positive guard tests
# ---------------------------------------------------------------------------

def test_blood_pressure_not_flagged_as_date():
    text = "Blood pressure 120/80 recorded at 9am."
    detections = detect(text)
    dates = [d for d in detections if d.entity_type == "DATE"]
    assert len(dates) == 0


def test_random_number_not_flagged_as_age():
    text = "Room 302, bed 4, floor 65."
    detections = detect(text)
    ages = [d for d in detections if d.entity_type == "AGE"]
    assert len(ages) == 0


def test_random_capitalized_words_not_flagged_as_address():
    text = "The New York Times reported on healthcare policy."
    detections = detect(text)
    addrs = [d for d in detections if d.entity_type == "ADDRESS"]
    assert len(addrs) == 0


# ---------------------------------------------------------------------------
# Full clinical note style integration test
# ---------------------------------------------------------------------------

def test_full_clinical_note():
    text = (
        "Patient John Doe, 65 years old, MRN: 1029384756, SSN 123-45-6789, "
        "residing at 742 Evergreen Terrace, contacted on 04/12/2025 via "
        "email john.doe@example.com or phone (555) 123-4567. "
        "Blood pressure 120/80, zip code 60614. "
        "Accessed from IP 192.168.1.10."
    )
    detections = detect(text)
    types_found = {d.entity_type for d in detections}
    expected = {
        "AGE", "MRN", "SSN", "ADDRESS", "DATE",
        "EMAIL", "PHONE", "ZIP", "IP_ADDRESS"
    }
    assert types_found == expected

    redacted = redact(text)
    assert "120/80" in redacted  # vitals must NOT be redacted
    assert "742 Evergreen Terrace" not in redacted
    assert "65 years old" not in redacted