"""
regex_detector.py
Member 2 - Detection Engine Lead
Week 1 / Day 2: Expanded regex detection.

Day 1 entities: PHONE, EMAIL, DATE, MRN
Day 2 adds:     SSN, ZIP, IP_ADDRESS
Day 2 also adds: overlap resolution (so DATE and MRN don't both grab
the same digits) and more false-positive guards.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Detection:
    entity_type: str
    text: str
    start: int
    end: int

    def __repr__(self):
        return f"Detection(type={self.entity_type}, text='{self.text}', span=({self.start},{self.end}))"


# ---------------------------------------------------------------------------
# Regex Patterns
# ---------------------------------------------------------------------------

PATTERNS = {
    "PHONE": re.compile(
        r"(?:\+?1[-.\s]?)?\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"
    ),

    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "DATE": re.compile(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|\d{4}-\d{1,2}-\d{1,2}"
        r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE
    ),

    "MRN": re.compile(
        r"\bMRN\s*[:#-]?\s*\d{6,10}\b",
        re.IGNORECASE
    ),

    # NEW Day 2 --------------------------------------------------------

    # SSN: 123-45-6789 (strict format, avoids matching plain phone-like numbers)
    "SSN": re.compile(
        r"\b\d{3}-\d{2}-\d{4}\b"
    ),

    # US ZIP code: 12345 or 12345-6789 — only matched near "zip"/"zip code"
    # context word to avoid catching random 5-digit numbers (like room numbers).
    "ZIP": re.compile(
        r"\b(?:zip\s*code|zip)\s*[:#-]?\s*(\d{5}(?:-\d{4})?)\b",
        re.IGNORECASE
    ),

    # IPv4 address
    "IP_ADDRESS": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),
}


def _resolve_overlaps(detections: List[Detection]) -> List[Detection]:
    """
    If two detections overlap in span (e.g. MRN pattern swallows part of
    a date, or SSN pattern overlaps a phone number), keep the longer match
    and drop the shorter one. Prevents duplicate/conflicting redactions.
    """
    if not detections:
        return detections

    sorted_dets = sorted(detections, key=lambda d: (d.start, -(d.end - d.start)))
    resolved: List[Detection] = []

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


def detect(text: str) -> List[Detection]:
    """
    Run all regex patterns against the input text, resolve overlaps,
    and return a sorted list of Detection objects.
    """
    results: List[Detection] = []

    for entity_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            # ZIP pattern has a capture group for the actual digits;
            # use the group span if present, else the whole match.
            if entity_type == "ZIP" and match.lastindex:
                start, end = match.start(1), match.end(1)
                matched_text = match.group(1)
            else:
                start, end = match.start(), match.end()
                matched_text = match.group()

            results.append(
                Detection(
                    entity_type=entity_type,
                    text=matched_text,
                    start=start,
                    end=end,
                )
            )

    return _resolve_overlaps(results)


def redact(text: str) -> str:
    detections = detect(text)
    redacted = text
    for d in sorted(detections, key=lambda x: x.start, reverse=True):
        redacted = redacted[:d.start] + f"[{d.entity_type}]" + redacted[d.end:]
    return redacted


if __name__ == "__main__":
    sample = (
        "Patient John Doe, MRN: 1029384756, SSN 123-45-6789, "
        "contacted on 04/12/2025 via email john.doe@example.com or "
        "phone (555) 123-4567. Address zip code 60614. "
        "Accessed from IP 192.168.1.10. "
        "Follow-up scheduled for January 5, 2026."
    )

    print("Original:")
    print(sample)
    print("\nDetections:")
    for d in detect(sample):
        print(" ", d)

    print("\nRedacted:")
    print(redact(sample))