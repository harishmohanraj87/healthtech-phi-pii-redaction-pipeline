"""
nlp_detector.py
Yash Kulkarni - Detection Engine Lead
Week 2 / Day 4: NLP-based PHI/PII detection using Microsoft Presidio + spaCy.

This complements regex_detector.py — regex catches structured entities
(phone, email, dates, MRN, SSN...), NLP catches unstructured/free-text
entities like PERSON names, LOCATION, and ORGANIZATION mentioned in
clinical notes.

CRITICAL REQUIREMENT (from team roadmap):
  "Parkinson Disease" and similar medical condition names must NOT be
  redacted as if they were a patient's name. Presidio's default PERSON
  recognizer can false-positive on capitalized medical terms because
  they look like proper nouns to the underlying NER model.

  This module fixes that with a MEDICAL_TERM_ALLOWLIST: any detected
  PERSON entity that matches (or is contained in) a known medical
  condition/disease name is filtered out before returning results.

SETUP (run locally, not in this sandbox — no internet access here):
    pip install presidio-analyzer presidio-anonymizer spacy --break-system-packages
    python -m spacy download en_core_web_lg
"""

from dataclasses import dataclass
from typing import List

try:
    from presidio_analyzer import AnalyzerEngine
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
    score: float  # Presidio confidence score (0.0 - 1.0)

    def __repr__(self):
        return (f"NlpDetection(type={self.entity_type}, text='{self.text}', "
                f"span=({self.start},{self.end}), score={self.score:.2f})")


# ---------------------------------------------------------------------------
# Medical term allowlist — terms that must NEVER be redacted as PERSON,
# even though they look like proper nouns (e.g. "Parkinson", "Alzheimer").
#
# Imported from medical_terms.py (Week 3 / Day 8) so there's a single
# source of truth for the allowlist instead of two lists drifting apart.
# ---------------------------------------------------------------------------

# Disease/condition keywords that, if found near a flagged PERSON entity,
# suggest it's a medical term rather than a patient name (e.g. "disease",
# "syndrome", "disorder" following the name).
MEDICAL_CONTEXT_WORDS = {"disease", "syndrome", "disorder", "diagnosis"}


def _is_medical_term(text: str, full_text: str, start: int, end: int) -> bool:
    """
    Returns True if a detected PERSON entity is actually a medical term
    and should be excluded from redaction.
    """
    lowered = text.strip().lower()

    # Direct allowlist match (handles "Parkinson", "Parkinson's", etc.)
    if lowered in MEDICAL_TERM_ALLOWLIST:
        return True

    # Check if any allowlist term is a substring (handles "Parkinson Disease")
    for term in MEDICAL_TERM_ALLOWLIST:
        if term in lowered:
            return True

    # Check the word immediately following the match for medical context
    # e.g. "Parkinson Disease" -> PERSON match might just be "Parkinson",
    # but "Disease" follows it.
    trailing_text = full_text[end:end + 20].strip().lower()
    first_word = trailing_text.split(" ")[0].strip(".,;:") if trailing_text else ""
    if first_word in MEDICAL_CONTEXT_WORDS:
        return True

    return False


class NlpDetector:
    """
    Wraps Presidio's AnalyzerEngine and filters out medical-term
    false positives from PERSON detections.
    """

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
        """
        Run Presidio NLP analysis on text and return filtered detections.

        entities: optional list of Presidio entity types to look for.
                  Defaults to PERSON, LOCATION, ORGANIZATION.
        """
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
                continue  # skip — it's a medical term, not a patient name

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
        print("Install locally with:")
        print("  pip install presidio-analyzer presidio-anonymizer spacy --break-system-packages")
        print("  python -m spacy download en_core_web_lg")
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