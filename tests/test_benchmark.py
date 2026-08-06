"""
test_benchmark.py

Tests performance metrics exposed by the pipeline.
"""

from app.services.pipeline import RedactionPipeline
from benchmark.sample_notes import SAMPLE_NOTE


def test_pipeline_returns_metrics():

    pipeline = RedactionPipeline()

    result = pipeline.process(
        SAMPLE_NOTE,
        return_metrics=True
    )

    assert "metrics" in result


def test_metrics_are_positive():

    pipeline = RedactionPipeline()

    result = pipeline.process(
        SAMPLE_NOTE,
        return_metrics=True
    )

    metrics = result["metrics"]

    assert metrics["detection_ms"] >= 0
    assert metrics["vault_ms"] >= 0
    assert metrics["total_ms"] > 0


def test_entities_detected():

    pipeline = RedactionPipeline()

    result = pipeline.process(
        SAMPLE_NOTE,
        return_metrics=True
    )

    assert result["metrics"]["entities_detected"] > 0