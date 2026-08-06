"""
benchmark_pipeline.py

Benchmarks the complete PHI/PII Redaction Pipeline.
"""

import time

from app.services.pipeline import RedactionPipeline
from benchmark.sample_notes import SAMPLE_NOTE


def benchmark_pipeline(iterations=10):
    pipeline = RedactionPipeline()

    # Warm-up (not measured)
    pipeline.process(SAMPLE_NOTE)

    execution_times = []
    latest_metrics = None
    latest_result = None

    for _ in range(iterations):

        start = time.perf_counter()

        latest_result = pipeline.process(
            SAMPLE_NOTE,
            return_metrics=True
        )

        end = time.perf_counter()

        execution_times.append((end - start) * 1000)
        latest_metrics = latest_result["metrics"]

    avg_time = sum(execution_times) / len(execution_times)
    fastest = min(execution_times)
    slowest = max(execution_times)

    throughput = len(SAMPLE_NOTE) / (avg_time / 1000)

    print("\n" + "=" * 60)
    print("HEALTHTECH PHI/PII PIPELINE PERFORMANCE REPORT")
    print("=" * 60)

    print(f"Iterations           : {iterations}")
    print(f"Document Size        : {len(SAMPLE_NOTE)} characters")
    print(f"Entities Detected    : {latest_metrics['entities_detected']}")

    print("-" * 60)

    print(f"Average Latency      : {avg_time:.2f} ms")
    print(f"Fastest Run          : {fastest:.2f} ms")
    print(f"Slowest Run          : {slowest:.2f} ms")

    print("-" * 60)

    print("Pipeline Breakdown")

    print(f"Detection Engine     : {latest_metrics['detection_ms']} ms")
    print(f"Redis Token Vault    : {latest_metrics['vault_ms']} ms")
    print(f"Total Pipeline       : {latest_metrics['total_ms']} ms")

    print("-" * 60)

    print(f"Throughput           : {throughput:,.0f} chars/sec")

    print("=" * 60)


if __name__ == "__main__":
    benchmark_pipeline()