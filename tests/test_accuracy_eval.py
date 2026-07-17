"""
test_accuracy_eval.py
Yash Kulkarni - Detection Engine Lead
Week 3 / Day 7: Tests validating the accuracy evaluation framework
and enforcing minimum accuracy thresholds.

This acts as a regression guard: if a future change to regex_detector.py
drops precision/recall below acceptable thresholds, this test fails and
flags it immediately.

Run with: pytest tests/test_accuracy_eval.py -v
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from detectors.accuracy_eval import evaluate, DATASET


# Minimum acceptable thresholds for the regex detection engine.
# These are intentionally strict since regex is a deterministic,
# structured-entity layer — we expect near-perfect accuracy here.
MIN_PRECISION = 0.95
MIN_RECALL = 0.95
MIN_F1 = 0.95


def test_dataset_is_not_empty():
    assert len(DATASET) > 0


def test_dataset_covers_all_entity_types():
    all_types = set()
    for case in DATASET:
        for entity_type, _ in case.expected:
            all_types.add(entity_type)

    expected_types = {
        "PHONE", "EMAIL", "DATE", "MRN", "SSN",
        "ZIP", "IP_ADDRESS", "ADDRESS", "AGE"
    }
    missing = expected_types - all_types
    assert not missing, f"Dataset is missing coverage for: {missing}"


def test_precision_meets_threshold():
    results = evaluate()
    assert results["precision"] >= MIN_PRECISION, (
        f"Precision {results['precision']*100:.1f}% is below "
        f"the {MIN_PRECISION*100:.0f}% threshold"
    )


def test_recall_meets_threshold():
    results = evaluate()
    assert results["recall"] >= MIN_RECALL, (
        f"Recall {results['recall']*100:.1f}% is below "
        f"the {MIN_RECALL*100:.0f}% threshold"
    )


def test_f1_meets_threshold():
    results = evaluate()
    assert results["f1"] >= MIN_F1, (
        f"F1 score {results['f1']*100:.1f}% is below "
        f"the {MIN_F1*100:.0f}% threshold"
    )


def test_no_trap_violations():
    results = evaluate()
    assert results["trap_violations"] == [], (
        f"Found {len(results['trap_violations'])} trap violations: "
        f"{results['trap_violations']}"
    )


def test_zero_false_positives_on_current_dataset():
    # Regex detector should currently be perfectly precise on this
    # curated dataset. If this ever fails, it means a pattern got
    # too aggressive and started over-matching.
    results = evaluate()
    assert results["false_positives"] == 0
