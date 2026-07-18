"""
nlp_detector.py
Yash Kulkarni - Detection Engine Lead
Week 2 / Day 4: NLP-based PHI/PII detection using Microsoft Presidio + spaCy,
extended with custom recognizers.

This complements regex_detector.py — regex catches structured entities
(phone, email, dates, MRN, SSN...), NLP catches unstructured/free-text
entities like PERSON names, LOCATION, and ORGANIZATION mentioned in
clinical notes.

Custom recognizers added on top of Presidio's built-ins:
  - MRN: Presidio has no built-in Medical Record Number entity, so a
    custom PatternRecognizer teaches it one, with context words
    ("mrn", "medical record") boosting confidence.
  - MEDICAL_TERM: an internal-only recognizer that flags known disease/
    condition names (Parkinson, Alzheimer's, Crohn's, etc.). It is never
    returned as a redaction target itself — it exists purely to cross-
    check overlapping PERSON detections and suppress false positives.

CRITICAL REQUIREMENT (from team roadmap):
  "Parkinson Disease" and similar medical condition names must NOT be
  redacted as if they were a patient's name. Presidio's default PERSON
  recognizer can false-positive on capitalized medical terms because
  they look like proper nouns to the underlying NER model.

  This module fixes that two ways:
    1. A MEDICAL_TERM_ALLOWLIST checked directly against any PERSON match
       (string-level check, works even without the custom recognizer).
    2. The custom MEDICAL_TERM recognizer above, which cross-checks
       overlapping spans for a second layer of protection.

SETUP (run locally, not in this sandbox — no internet access here):
    pip install presidio-analyzer presidio-anonymizer spacy --break-system-packages
    python -m spacy download en_core_web_lg
"""

from dataclasses import dataclass
from typing import List, Set

try:
    from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern  # type: ignore
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False


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
# Day 8: expanded from ~10 entries to a full reference covering 30+
# eponymous conditions and general syndrome names, now maintained in
# its own module (medical_terms.py) for easier upkeep.
# ---------------------------------------------------------------------------

from detectors.medical_terms import MEDICAL_TERM_ALLOWLIST, MEDICAL_CONTEXT_WORDS


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


def _build_mrn_recognizer():
    """
    Custom Presidio PatternRecognizer for Medical Record Numbers.
    Presidio has no built-in MRN entity, so we teach it one using the
    same pattern logic as our regex detector, but wired into Presidio's
    NLP pipeline so it benefits from context-aware scoring.
    """
    pattern = Pattern(
        name="mrn_pattern",
        regex=r"\bMRN\s*[:#-]?\s*\d{6,10}\b",
        score=0.9,
    )
    return PatternRecognizer(
        supported_entity="MRN",
        patterns=[pattern],
        context=["mrn", "medical record", "record number"],
    )


def _build_medical_denylist_recognizer():
    """
    Custom Presidio recognizer that explicitly flags known medical
    condition names as a distinct MEDICAL_TERM entity type. Having
    Presidio recognize these as their own entity (rather than relying
    solely on post-filtering PERSON results) makes the allowlist logic
    more robust and visible in Presidio's own output.
    """
    terms = [t.title() for t in MEDICAL_TERM_ALLOWLIST if "'" not in t]
    pattern = Pattern(
        name="medical_term_pattern",
        regex=r"\b(?:" + "|".join(terms) + r")\b",
        score=0.85,
    )
    return PatternRecognizer(
        supported_entity="MEDICAL_TERM",
        patterns=[pattern],
    )


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

        # Register custom recognizers on top of Presidio's built-ins
        self.analyzer.registry.add_recognizer(_build_mrn_recognizer())
        self.analyzer.registry.add_recognizer(_build_medical_denylist_recognizer())

    def detect(self, text: str, entities: List[str] = None) -> List[NlpDetection]:
        """
        Run Presidio NLP analysis on text and return filtered detections.

        entities: optional list of Presidio entity types to look for.
                  Defaults to PERSON, LOCATION, ORGANIZATION, MRN.
                  MEDICAL_TERM is always analyzed internally (to protect
                  overlapping PERSON matches) but never returned/redacted.
        """
        if entities is None:
            entities = ["PERSON", "LOCATION", "ORGANIZATION", "MRN"]

        # Always include MEDICAL_TERM in the analysis pass so we can use
        # its spans to double-check PERSON overlaps, even if the caller
        # didn't ask for it.
        analyze_entities = list(set(entities) | {"MEDICAL_TERM"})

        results = self.analyzer.analyze(
            text=text,
            entities=analyze_entities,
            language=self.language,
        )

        # Collect medical term spans first so we can cross-check overlaps
        medical_spans = [
            (r.start, r.end) for r in results if r.entity_type == "MEDICAL_TERM"
        ]

        def _overlaps_medical_span(start: int, end: int) -> bool:
            return any(start < m_end and end > m_start for m_start, m_end in medical_spans)

        detections: List[NlpDetection] = []
        for r in results:
            if r.entity_type == "MEDICAL_TERM":
                continue  # internal-only, never returned as a redaction target

            if r.entity_type not in entities:
                continue  # caller didn't ask for this type

            matched_text = text[r.start:r.end]

            if r.entity_type == "PERSON" and (
                _is_medical_term(matched_text, text, r.start, r.end)
                or _overlaps_medical_span(r.start, r.end)
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
            "John Doe, MRN: 1029384756, was diagnosed with Parkinson Disease "
            "last year. He was referred to Dr. Sarah Chen at Mercy General Hospital."
        )
        print("Original:")
        print(sample)
        print("\nDetections:")
        for d in detector.detect(sample):
            print(" ", d)