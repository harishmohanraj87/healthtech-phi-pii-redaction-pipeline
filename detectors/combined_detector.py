"""
combined_detector.py

Unified detection interface combining the Regex and NLP detection layers.

Regex handles structured PHI/PII:
    PHONE, EMAIL, DATE, MRN, SSN, ZIP, IP_ADDRESS, ADDRESS, AGE

NLP handles unstructured entities:
    PERSON, LOCATION, ORGANIZATION

The combined detector:
    1. Runs Regex detection.
    2. Runs NLP detection when Presidio is available.
    3. Merges both results.
    4. Gives Regex priority over NLP when spans overlap.
    5. Removes duplicate/overlapping detections.
    6. Returns detections sorted by position.
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
        return (
            f"CombinedDetection("
            f"type={self.entity_type}, "
            f"text='{self.text}', "
            f"span=({self.start},{self.end}), "
            f"source={self.source})"
        )


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
        Run Regex + NLP detection and return a clean,
        deduplicated list of detections.
        """

        results: List[CombinedDetection] = []

        # ==========================================
        # 1. REGEX DETECTION
        # ==========================================

        regex_results = regex_detect(text)

        for detection in regex_results:

            results.append(
                CombinedDetection(
                    entity_type=detection.entity_type,
                    text=detection.text,
                    start=detection.start,
                    end=detection.end,
                    source="regex",
                )
            )

        # ==========================================
        # 2. NLP DETECTION
        # ==========================================

        if self._nlp_detector is not None:

            nlp_results = self._nlp_detector.detect(text)

            for detection in nlp_results:

                results.append(
                    CombinedDetection(
                        entity_type=detection.entity_type,
                        text=detection.text,
                        start=detection.start,
                        end=detection.end,
                        source="nlp",
                    )
                )

        # ==========================================
        # 3. RESOLVE OVERLAPS
        # ==========================================

        return self._resolve_cross_layer_overlaps(results)

    def _resolve_cross_layer_overlaps(
        self,
        detections: List[CombinedDetection],
    ) -> List[CombinedDetection]:
        """
        Resolve overlapping detections.

        Priority:

            Regex > NLP

        If two detections from the same source overlap:

            Longer span > shorter span

        Example:

            NLP:
                PERSON -> "john"

            Regex:
                EMAIL -> "john@example.com"

        Result:

            EMAIL -> "john@example.com"

        The overlapping PERSON detection is removed.
        """

        if not detections:
            return []

        # ------------------------------------------
        # Sort by:
        #
        # 1. Start position
        # 2. Regex before NLP
        # 3. Longer span first
        # ------------------------------------------

        def sort_key(detection: CombinedDetection):

            source_priority = (
                0 if detection.source == "regex" else 1
            )

            span_length = detection.end - detection.start

            return (
                detection.start,
                source_priority,
                -span_length,
            )

        sorted_detections = sorted(
            detections,
            key=sort_key,
        )

        resolved: List[CombinedDetection] = []

        for detection in sorted_detections:

            has_overlap = False

            for kept in resolved:

                overlap = (
                    detection.start < kept.end
                    and detection.end > kept.start
                )

                if not overlap:
                    continue

                # ----------------------------------
                # Regex always wins over NLP
                # ----------------------------------

                if (
                    detection.source == "nlp"
                    and kept.source == "regex"
                ):
                    has_overlap = True
                    break

                if (
                    detection.source == "regex"
                    and kept.source == "nlp"
                ):
                    # Remove the NLP detection that was
                    # previously kept.
                    resolved.remove(kept)
                    break

                # ----------------------------------
                # Same source:
                # Keep the longer span.
                # ----------------------------------

                if detection.source == kept.source:

                    detection_length = (
                        detection.end - detection.start
                    )

                    kept_length = (
                        kept.end - kept.start
                    )

                    if detection_length <= kept_length:
                        has_overlap = True
                        break

                    resolved.remove(kept)
                    break

            if not has_overlap:
                resolved.append(detection)

        # Final ordering
        resolved.sort(
            key=lambda d: d.start
        )

        return resolved

    def redact(self, text: str) -> str:
        """
        Convenience redaction method.

        Replaces detected entities with:

            [ENTITY_TYPE]

        The production pipeline uses the Token Vault instead.
        """

        detections = self.detect(text)

        redacted = text

        # Replace from right to left so indexes remain valid.
        for detection in sorted(
            detections,
            key=lambda x: x.start,
            reverse=True,
        ):

            redacted = (
                redacted[:detection.start]
                + f"[{detection.entity_type}]"
                + redacted[detection.end:]
            )

        return redacted


if __name__ == "__main__":

    detector = CombinedDetector()

    sample = (
        "Patient John Doe, 65 years old, "
        "MRN: 1029384756, "
        "SSN 123-45-6789, "
        "residing at 742 Evergreen Terrace, "
        "was diagnosed with Parkinson Disease. "
        "Contacted on 04/12/2025 via email "
        "john.doe@example.com or phone "
        "(555) 123-4567. "
        "Referred to Dr. Sarah Chen at "
        "Mercy General Hospital."
    )

    print("Original:")
    print(sample)

    print("\nCombined Detections:")

    for detection in detector.detect(sample):
        print(" ", detection)

    print("\nRedacted:")

    print(detector.redact(sample))