"""
test_restore.py

Tests for restoring secure tokens back to
their original PHI values.
"""

from app.services.pipeline import RedactionPipeline


def test_restore_single_token():
    """
    Verify that a single token is restored correctly.
    """

    pipeline = RedactionPipeline()

    token = pipeline.vault.get_or_create_token(
        "PERSON",
        "John Doe"
    )

    restored = pipeline.restore(
        f"Patient {token}"
    )

    assert restored == "Patient John Doe"


def test_restore_multiple_tokens():
    """
    Verify multiple tokens can be restored.
    """

    pipeline = RedactionPipeline()

    person = pipeline.vault.get_or_create_token(
        "PERSON",
        "John Doe"
    )

    email = pipeline.vault.get_or_create_token(
        "EMAIL",
        "john@example.com"
    )

    restored = pipeline.restore(
        f"{person} - {email}"
    )

    assert restored == "John Doe - john@example.com"


def test_unknown_token():
    """
    Unknown tokens should remain unchanged.
    """

    pipeline = RedactionPipeline()

    restored = pipeline.restore(
        "Patient [PERSON_UNKNOWN]"
    )

    assert restored == "Patient [PERSON_UNKNOWN]"