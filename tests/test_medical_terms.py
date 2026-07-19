"""
test_medical_terms.py
Yash Kulkarni - Detection Engine Lead
Week 3 / Day 8: Tests for the expanded medical term reference list.

Run with: pytest tests/test_medical_terms.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.medical_terms import (
    MEDICAL_TERM_ALLOWLIST,
    is_known_medical_term,
    contains_medical_term,
)
from detectors.nlp_detector import _is_medical_term


def test_allowlist_has_substantial_coverage():
    # Day 8 goal: grow from ~10 to 30+ conditions
    assert len(MEDICAL_TERM_ALLOWLIST) >= 30


def test_original_core_conditions_still_present():
    for term in ["parkinson", "alzheimer's", "crohn's", "down syndrome"]:
        assert term in MEDICAL_TERM_ALLOWLIST


def test_new_eponymous_conditions_added():
    for term in ["turner's", "marfan", "cushing's", "kawasaki"]:
        assert term in MEDICAL_TERM_ALLOWLIST


def test_is_known_medical_term_exact_match():
    assert is_known_medical_term("Parkinson's") is True
    assert is_known_medical_term("parkinson's") is True  # case-insensitive


def test_is_known_medical_term_rejects_real_name():
    assert is_known_medical_term("John Doe") is False


def test_contains_medical_term_substring_match():
    assert contains_medical_term("Diagnosed with Parkinson Disease") is True


def test_contains_medical_term_rejects_unrelated_text():
    assert contains_medical_term("Patient walked into the room") is False


# ---------------------------------------------------------------------------
# Integration: nlp_detector's _is_medical_term using the expanded list
# ---------------------------------------------------------------------------

def test_turner_syndrome_via_context_word():
    text = "Turner syndrome noted in chart."
    start = text.index("Turner")
    end = start + len("Turner")
    assert _is_medical_term("Turner", text, start, end) is True


def test_marfan_direct_allowlist_match():
    text = "History of Marfan's noted."
    start = text.index("Marfan's")
    end = start + len("Marfan's")
    assert _is_medical_term("Marfan's", text, start, end) is True


def test_guillain_barre_syndrome():
    text = "Diagnosed with Guillain-Barre syndrome last month."
    start = text.index("Guillain-Barre")
    end = start + len("Guillain-Barre")
    assert _is_medical_term("Guillain-Barre", text, start, end) is True


def test_real_patient_name_not_caught_by_expanded_list():
    text = "Patient John Morrison admitted today."
    start = text.index("John Morrison")
    end = start + len("John Morrison")
    assert _is_medical_term("John Morrison", text, start, end) is False
