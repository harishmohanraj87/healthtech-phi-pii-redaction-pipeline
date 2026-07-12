"""
test_regex_detector.py
Member 2 - Detection Engine Lead
Week 1 / Day 1: Initial test cases for regex_detector.py

Run with: pytest tests/test_regex_detector.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.regex_detector import detect, redact


# ---------------------------------------------------------------------------
# PHONE tests
# ---------------------------------------------------------------------------

def test_phone_dash_format():
    text = "Call me at 555-123-4567 tomorrow."
    detections = detect(text)
    phones = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phones) == 1
    assert phones[0].text == "555-123-4567"


def test_phone_parens_format():
    text = "Contact: (555) 123-4567"
    detections = detect(text)
    phones = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phones) == 1


def test_phone_with_country_code():
    text = "Reach me at +1 555-123-4567 anytime."
    detections = detect(text)
    phones = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phones) == 1


# ---------------------------------------------------------------------------
# EMAIL tests
# ---------------------------------------------------------------------------

def test_email_basic():
    text = "Send records to john.doe@example.com please."
    detections = detect(text)
    emails = [d for d in detections if d.entity_type == "EMAIL"]
    assert len(emails) == 1
    assert emails[0].text == "john.doe@example.com"


def test_email_with_subdomain():
    text = "Email: patient.records@clinic.hospital.org"
    detections = detect(text)
    emails = [d for d in detections if d.entity_type == "EMAIL"]
    assert len(emails) == 1


# ---------------------------------------------------------------------------
# DATE tests
# ---------------------------------------------------------------------------

def test_date_slash_format():
    text = "Appointment on 04/12/2025 confirmed."
    detections = detect(text)
    dates = [d for d in detections if d.entity_type == "DATE"]
    assert len(dates) == 1
    assert dates[0].text == "04/12/2025"


def test_date_iso_format():
    text = "Recorded on 2025-04-12 in the system."
    detections = detect(text)
    dates = [d for d in detections if d.entity_type == "DATE"]
    assert len(dates) == 1


def test_date_written_format():
    text = "Follow-up scheduled for January 5, 2026."
    detections = detect(text)
    dates = [d for d in detections if d.entity_type == "DATE"]
    assert len(dates) == 1


# ---------------------------------------------------------------------------
# MRN tests
# ---------------------------------------------------------------------------

def test_mrn_with_colon():
    text = "Patient MRN: 1029384756 was admitted yesterday."
    detections = detect(text)
    mrns = [d for d in detections if d.entity_type == "MRN"]
    assert len(mrns) == 1
    assert "1029384756" in mrns[0].text


def test_mrn_without_colon():
    text = "MRN 5647382910 flagged for review."
    detections = detect(text)
    mrns = [d for d in detections if d.entity_type == "MRN"]
    assert len(mrns) == 1


# ---------------------------------------------------------------------------
# False-positive guard tests (important for accuracy tuning later)
# ---------------------------------------------------------------------------

def test_no_false_positive_on_plain_number():
    text = "The patient's blood pressure was 120/80 today."
    detections = detect(text)
    dates = [d for d in detections if d.entity_type == "DATE"]
    assert len(dates) == 0  # 120/80 should NOT be caught as a date


def test_no_false_positive_on_short_number():
    text = "Room number 4567, bed 2."
    detections = detect(text)
    phones = [d for d in detections if d.entity_type == "PHONE"]
    assert len(phones) == 0


# ---------------------------------------------------------------------------
# Combined / integration-style test
# ---------------------------------------------------------------------------

def test_combined_detection_and_redaction():
    text = (
        "Patient John Doe, MRN: 1029384756, contacted on 04/12/2025 via "
        "email john.doe@example.com or phone (555) 123-4567."
    )
    detections = detect(text)
    types_found = {d.entity_type for d in detections}
    assert types_found == {"MRN", "DATE", "EMAIL", "PHONE"}

    redacted = redact(text)
    assert "john.doe@example.com" not in redacted
    assert "1029384756" not in redacted
    assert "[EMAIL]" in redacted
    assert "[MRN]" in redacted
    assert "[DATE]" in redacted
    assert "[PHONE]" in redacted
