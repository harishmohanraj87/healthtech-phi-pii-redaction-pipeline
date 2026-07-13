"""
test_regex_detector.py
Member 2 - Detection Engine Lead
Week 1 / Day 2: Tests for SSN, ZIP, IP_ADDRESS + overlap resolution.

Run with: pytest tests/test_regex_detector.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.regex_detector import detect, redact


# ---------------------------------------------------------------------------
# SSN tests
# ---------------------------------------------------------------------------

def test_ssn_basic():
    text = "Patient SSN is 123-45-6789 on file."
    detections = detect(text)
    ssns = [d for d in detections if d.entity_type == "SSN"]
    assert len(ssns) == 1
    assert ssns[0].text == "123-45-6789"


def test_ssn_not_confused_with_phone():
    text = "SSN: 123-45-6789 and phone: 555-123-4567"
    detections = detect(text)
    ssns = [d for d in detections if d.entity_type == "SSN"]
    phones = [d for d in detections if d.entity_type == "PHONE"]
    assert len(ssns) == 1
    assert len(phones) == 1


# ---------------------------------------------------------------------------
# ZIP tests
# ---------------------------------------------------------------------------

def test_zip_basic():
    text = "Mailing address zip code 60614."
    detections = detect(text)
    zips = [d for d in detections if d.entity_type == "ZIP"]
    assert len(zips) == 1
    assert zips[0].text == "60614"


def test_zip_plus4():
    text = "Zip: 60614-1234"
    detections = detect(text)
    zips = [d for d in detections if d.entity_type == "ZIP"]
    assert len(zips) == 1
    assert zips[0].text == "60614-1234"


def test_zip_requires_context_word():
    # A random 5-digit number with no "zip" nearby should NOT be flagged
    text = "Room number 60614 was cleaned today."
    detections = detect(text)
    zips = [d for d in detections if d.entity_type == "ZIP"]
    assert len(zips) == 0


# ---------------------------------------------------------------------------
# IP_ADDRESS tests
# ---------------------------------------------------------------------------

def test_ip_basic():
    text = "Accessed patient record from IP 192.168.1.10."
    detections = detect(text)
    ips = [d for d in detections if d.entity_type == "IP_ADDRESS"]
    assert len(ips) == 1
    assert ips[0].text == "192.168.1.10"


def test_ip_invalid_octet_not_matched():
    # 999 is not a valid IP octet, should not fully match as IP
    text = "Value 999.999.999.999 is not a real IP."
    detections = detect(text)
    ips = [d for d in detections if d.entity_type == "IP_ADDRESS"]
    assert len(ips) == 0


# ---------------------------------------------------------------------------
# Overlap resolution tests
# ---------------------------------------------------------------------------

def test_mrn_and_date_no_overlap_conflict():
    text = "MRN: 1029384756 recorded on 04/12/2025."
    detections = detect(text)
    # Should get exactly one MRN and one DATE, no overlapping duplicates
    types = [d.entity_type for d in detections]
    assert types.count("MRN") == 1
    assert types.count("DATE") == 1


def test_no_duplicate_spans():
    text = (
        "Patient John Doe, MRN: 1029384756, SSN 123-45-6789, "
        "contacted on 04/12/2025 via email john.doe@example.com or "
        "phone (555) 123-4567."
    )
    detections = detect(text)
    spans = [(d.start, d.end) for d in detections]
    assert len(spans) == len(set(spans))  # no duplicate/overlapping spans


# ---------------------------------------------------------------------------
# Combined integration test
# ---------------------------------------------------------------------------

def test_combined_all_entities():
    text = (
        "Patient John Doe, MRN: 1029384756, SSN 123-45-6789, "
        "contacted on 04/12/2025 via email john.doe@example.com or "
        "phone (555) 123-4567. Address zip code 60614. "
        "Accessed from IP 192.168.1.10."
    )
    detections = detect(text)
    types_found = {d.entity_type for d in detections}
    assert types_found == {
        "MRN", "SSN", "DATE", "EMAIL", "PHONE", "ZIP", "IP_ADDRESS"
    }

    redacted = redact(text)
    assert "1029384756" not in redacted
    assert "123-45-6789" not in redacted
    assert "192.168.1.10" not in redacted
    assert "60614" not in redacted