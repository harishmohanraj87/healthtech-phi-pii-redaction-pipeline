"""
combined_detector.py
Yash Kulkarni - Detection Engine Lead
Week 2 / Day 5: Unified detection interface combining the regex layer
and the NLP layer into a single entry point.

Why this exists:
  regex_detector.py catches structured entities (PHONE, EMAIL, DATE,
  MRN, SSN, ZIP, IP_ADDRESS, ADDRESS, AGE).
  nlp_detector.py catches unstructured/free-text entities (PERSON,
  LOCATION, ORGANIZATION) using Presidio + spaCy.

  Member 1 (Technical Lead) will eventually wire the full pipeline
  (Regex -> NLP -> Vault -> Output), but having a single combined
  interface here makes it easy to test both layers together and hand
  off a clean function to Member 1 for integration.

This module:
  1. Runs both detectors on the same text.
  2. Normalizes both outputs into one common format.
  3. Resolves cross-layer overlaps (e.g. regex MRN pattern and NLP
     PERSON pattern both firing on overlapping text) by preferring the
     more specific/structured regex match over the NLP guess.
  4. Produces one clean, deduplicated list ready for the Token Vault.
"""

from dataclasses import dataclass
from typing import List

from detectors.regex_detector import detect as regex_detect
from detectors.nlp_detector import NlpDetector, PRESIDIO_AVAILABLE


@dataclass
class CombinedDetection:
    entity_type: str
    text: str
    start: int
    end: int
    source: str  # "regex" or "nlp"

    def __repr__(self):
        return (f"CombinedDetection(type={self.entity_type}, text='{self.text}', "
                f"span=({self.start},{self.end}), source={self.source})")


# Regex entities are structured/high-confidence, so they win any overlap
# against NLP guesses (e.g. don't let an NLP PERSON match eat into a
# regex MRN or DATE match that overlaps the same characters).
REGEX_PRIORITY_ENTITIES = {
    "PHONE", "EMAIL", "DATE", "MRN", "SSN", "ZIP", "IP_ADDRESS", "ADDRESS", "AGE"
}


class CombinedDetector:
    def __init__(self):
        self._nlp_detector = None
        if PRESIDIO_AVAILABLE:
            try:
                self._nlp_detector = NlpDetector()
            except ImportError:
                self._nlp_detector = None

    def detect(self, text: str) -> List[CombinedDetection]:
        """
        Run regex + NLP detection on text and return one merged,
        deduplicated list sorted by position.
        """
        results: List[CombinedDetection] = []

        # Layer 1: regex (structured entities)
        for d in regex_detect(text):
            results.append(
                CombinedDetection(
                    entity_type=d.entity_type,
                    text=d.text,
                    start=d.start,
                    end=d.end,
                    source="regex",
                )
            )

        # Layer 2: NLP (free-text entities) — only if Presidio is installed
        if self._nlp_detector is not None:
            for d in self._nlp_detector.detect(text):
                results.append(
                    CombinedDetection(
                        entity_type=d.entity_type,
                        text=d.text,
                        start=d.start,
                        end=d.end,
                        source="nlp",
                    )
                )

        return self._resolve_cross_layer_overlaps(results)

    def _resolve_cross_layer_overlaps(
        self, detections: List[CombinedDetection]
    ) -> List[CombinedDetection]:
        """
        If a regex match and an NLP match overlap the same text span,
        keep the regex one (it's structured/high-confidence) and drop
        the NLP one. If two matches from the same source overlap, keep
        the longer one.
        """
        if not detections:
            return detections

        def sort_key(d: CombinedDetection):
            # Regex entities sort first when starts are equal, so they
            # win ties during overlap resolution below.
            source_rank = 0 if d.entity_type in REGEX_PRIORITY_ENTITIES else 1
            return (d.start, source_rank, -(d.end - d.start))

        sorted_dets = sorted(detections, key=sort_key)
        resolved: List[CombinedDetection] = []

        for d in sorted_dets:
            overlaps_prev = False
            for kept in resolved:
                if d.start < kept.end and d.end > kept.start:
                    overlaps_prev = True
                    break
            if not overlaps_prev:
                resolved.append(d)

        resolved.sort(key=lambda d: d.start)
        return resolved

    def redact(self, text: str) -> str:
        """
        Convenience method for quick testing — replaces all detected
        entities with [ENTITY_TYPE] placeholders. The real pipeline will
        route through the Token Vault (Member 3) instead of this.
        """
        detections = self.detect(text)
        redacted = text
        for d in sorted(detections, key=lambda x: x.start, reverse=True):
            redacted = redacted[:d.start] + f"[{d.entity_type}]" + redacted[d.end:]
        return redacted


if __name__ == "__main__":
    detector = CombinedDetector()

    sample = (
        "Patient John Doe, 65 years old, MRN: 1029384756, SSN 123-45-6789, "
        "residing at 742 Evergreen Terrace, was diagnosed with Parkinson Disease. "
        "Contacted on 04/12/2025 via email john.doe@example.com or phone "
        "(555) 123-4567. Referred to Dr. Sarah Chen at Mercy General Hospital."
    )

    print("Original:")
    print(sample)
    print("\nCombined Detections:")
    for d in detector.detect(sample):
        print(" ", d)

    print("\nRedacted:")
    print(detector.redact(sample))
