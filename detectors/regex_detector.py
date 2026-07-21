"""
regex_detector.py
Yash Kulkarni - Detection Engine Lead
Week 1 / Day 1: Core regex detection for PHONE, EMAIL, DATE, and MRN entities.

This module scans raw clinical text and returns a list of detected PHI/PII
entities with their type, matched text, and character span (start, end).
Downstream (Week 2) this will feed into the NLP detector (Presidio/spaCy)
and then the Token Vault for placeholder replacement.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Detection:
    entity_type: str   # e.g. "PHONE", "EMAIL", "DATE", "MRN"
    text: str           # the actual matched substring
    start: int          # start index in original text
    end: int            # end index in original text

    def __repr__(self):
        return f"Detection(type={self.entity_type}, text='{self.text}', span=({self.start},{self.end}))"


# ---------------------------------------------------------------------------
# Regex Patterns
# ---------------------------------------------------------------------------

PATTERNS = {
    # US-style phone numbers: (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890
    "PHONE": re.compile(
        r"(?:\+?1[-.\s]?)?\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"
    ),

    # Standard email addresses
    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    # Dates: 12/31/2025, 12-31-2025, 2025-12-31, Jan 5 2025, January 5, 2025
    "DATE": re.compile(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|\d{4}-\d{1,2}-\d{1,2}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE
    ),

    # Medical Record Number: MRN followed by 6-10 digits (with optional colon/space)
    "MRN": re.compile(
        r"\bMRN\s*[:#-]?\s*\d{6,10}\b",
        re.IGNORECASE
    ),

    # Social Security Number: 123-45-6789 or 123 45 6789
    "SSN": re.compile(
        r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b"
    ),

    # US ZIP code: 60614 or 60614-1234 (only when preceded by "zip"/"zip code")
    "ZIP": re.compile(
        r"\bzip(?:\s*code)?\s*:?\s*(\d{5}(?:-\d{4})?)\b",
        re.IGNORECASE
    ),

    # IPv4 address
    "IP_ADDRESS": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),

    # Street address: number + street name + common suffix
    "ADDRESS": re.compile(
        r"\b\d{1,5}\s+[A-Za-z0-9.\s]+?\s(?:St|Street|Ave|Avenue|Blvd|Boulevard|"
        r"Rd|Road|Dr|Drive|Ln|Lane|Ct|Court|Terrace|Ter|Way|Pl|Place)\b\.?",
        re.IGNORECASE
    ),

    # Age: "65 years old", "65 y/o", "65-year-old", "Age: 42"
    "AGE": re.compile(
        r"\b\d{1,3}[\s-]?(?:years?[\s-]old|y/o|yo)\b|\bAge\s*:?\s*\d{1,3}\b",
        re.IGNORECASE
    ),
}


def detect(text: str) -> List[Detection]:
    """
    Run all regex patterns against the input text and return a combined,
    sorted (by start index) list of Detection objects.
    """
    results: List[Detection] = []

    for entity_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            # If the pattern defines a capture group (e.g. ZIP, where the
            # label "zip code" shouldn't be part of the redacted span),
            # use that group's span instead of the whole match.
            if match.lastindex:
                span_start, span_end = match.start(1), match.end(1)
            else:
                span_start, span_end = match.start(), match.end()
            results.append(
                Detection(
                    entity_type=entity_type,
                    text=text[span_start:span_end],
                    start=span_start,
                    end=span_end,
                )
            )

    # Sort by position in text so output reads naturally top-to-bottom
    results.sort(key=lambda d: d.start)
    return results


def redact(text: str) -> str:
    """
    Quick utility (not final pipeline behavior, just for Day 1 sanity checks)
    that replaces detected entities with [ENTITY_TYPE] placeholders.
    Real placeholder/token logic will live in Member 3's Token Vault.
    """
    detections = detect(text)
    # Replace from the end backwards so indices don't shift
    redacted = text
    for d in sorted(detections, key=lambda x: x.start, reverse=True):
        redacted = redacted[:d.start] + f"[{d.entity_type}]" + redacted[d.end:]
    return redacted


if __name__ == "__main__":
    sample = (
        "Patient John Doe, MRN: 1029384756, contacted on 04/12/2025 via "
        "email john.doe@example.com or phone (555) 123-4567. "
        "Follow-up scheduled for January 5, 2026."
    )

    print("Original:")
    print(sample)
    print("\nDetections:")
    for d in detect(sample):
        print(" ", d)

    print("\nRedacted:")
    print(redact(sample))