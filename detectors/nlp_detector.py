"""
nlp_detector.py
Member 2 - Detection Engine Lead
Week 2 / Day 4: NLP-based PHI/PII detection using Microsoft Presidio + spaCy.

This complements regex_detector.py — regex catches structured entities
(phone, email, dates, MRN, SSN...), NLP catches unstructured/free-text
entities like PERSON names, LOCATION, and ORGANIZATION mentioned in
clinical notes.

CRITICAL REQUIREMENT (from team roadmap):
  "Parkinson Disease" and similar medical condition names must NOT be
  redacted as if they were a patient's name.

SETUP:
    pip install presidio-analyzer presidio-anonymizer spacy --break-system-packages
    python -m spacy download en_core_web_lg
"""

from dataclasses import dataclass
from typing import List, Set

try:
    from presidio_analyzer import AnalyzerEngine  # type: ignore
    from presidio_analyzer.nlp_engine import NlpEngineProvider  # type: ignore
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False

from detectors.medical_terms import MEDICAL_TERM_ALLOWLIST


@dataclass
class NlpDetection:
    entity_type: str
    text: str
    start: int
    end: int
    score: float

    def __repr__(self):
        return (f"NlpDetection(type={self.entity_type}, text='{self.text}', "
                f"span=({self.start},{self.end}), score={self.score:.2f})")


MEDICAL_CONTEXT_WORDS = {"disease", "syndrome", "disorder", "diagnosis"}


def _is_medical_term(text: str, full_text: str, start: int, end: int) -> bool:
    lowered = text.strip().lower()

    if lowered in MEDICAL_TERM_ALLOWLIST:
        return True

    for term in MEDICAL_TERM_ALLOWLIST:
        if term in lowered:
            return True

    trailing_text = full_text[end:end + 20].strip().lower()
    first_word = trailing_text.split(" ")[0].strip(".,;:") if trailing_text else ""
    if first_word in MEDICAL_CONTEXT_WORDS:
        return True

    return False


class NlpDetector:
    def __init__(self, language: str = "en"):
        if not PRESIDIO_AVAILABLE:
            raise ImportError(
                "presidio-analyzer is not installed. Run:\n"
                "  pip install presidio-analyzer presidio-anonymizer spacy --break-system-packages\n"
                "  python -m spacy download en_core_web_lg"
            )
        self.language = language
        self.analyzer = AnalyzerEngine()

    def detect(self, text: str, entities: List[str] = None) -> List[NlpDetection]:
        if entities is None:
            entities = ["PERSON", "LOCATION", "ORGANIZATION"]

        results = self.analyzer.analyze(
            text=text,
            entities=entities,
            language=self.language,
        )

        detections: List[NlpDetection] = []
        for r in results:
            matched_text = text[r.start:r.end]

            if r.entity_type == "PERSON" and _is_medical_term(
                matched_text, text, r.start, r.end
            ):
                continue

            detections.append(
                NlpDetection(
                    entity_type=r.entity_type,
                    text=matched_text,
                    start=r.start,
                    end=r.end,
                    score=r.score,
                )
            )

        detections.sort(key=lambda d: d.start)
        return detections


if __name__ == "__main__":
    if not PRESIDIO_AVAILABLE:
        print("Presidio not installed in this environment.")
    else:
        detector = NlpDetector()
        sample = (
            "John Doe was diagnosed with Parkinson Disease last year. "
            "He was referred to Dr. Sarah Chen at Mercy General Hospital."
        )
        print("Original:")
        print(sample)
        print("\nDetections:")
        for d in detector.detect(sample):
            print(" ", d)