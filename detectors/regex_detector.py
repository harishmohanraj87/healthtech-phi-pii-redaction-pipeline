"""
regex_detector.py
Member 2 - Detection Engine Lead
Week 1 / Day 3: Edge-case hardening + 2 more entity types.

Entities so far:
  Day 1: PHONE, EMAIL, DATE, MRN
  Day 2: SSN, ZIP, IP_ADDRESS
  Day 3: ADDRESS, AGE

Day 3 also fixes an edge case where DATE patterns could false-positive on
plain age mentions like "65 years old" or vitals like "120/80", and adds
a simple street-address pattern (common in clinical intake notes).
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

    "SSN": re.compile(
        r"\b\d{3}-\d{2}-\d{4}\b"
    ),

    "ZIP": re.compile(
        r"\b(?:zip\s*code|zip)\s*[:#-]?\s*(\d{5}(?:-\d{4})?)\b",
        re.IGNORECASE
    ),

    "IP_ADDRESS": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),

    # NEW Day 3 ----------------------------------------------------------

    # Simple US street address: number + street name + common suffix
    # e.g. "742 Evergreen Terrace", "1600 Pennsylvania Ave"
    "ADDRESS": re.compile(
        r"\b\d{1,5}\s+[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\s+"
        r"(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ln|Lane|Dr|Drive|"
        r"Ct|Court|Way|Terrace|Ter|Pl|Place|Cir|Circle|Pkwy|Parkway)\b"
    ),

    # Age: "65 years old", "65-year-old", "age 65" — context word required
    # so we don't grab every stray number in the text.
    "AGE": re.compile(
        r"\b(?:\d{1,3}\s*-?\s*years?\s*-?\s*old|age\s*[:#-]?\s*\d{1,3})\b",
        re.IGNORECASE
    ),
}


def _resolve_overlaps(detections: List[Detection]) -> List[Detection]:
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
    results: List[Detection] = []

    for entity_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
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
        "Patient John Doe, 65 years old, MRN: 1029384756, SSN 123-45-6789, "
        "residing at 742 Evergreen Terrace, contacted on 04/12/2025 via "
        "email john.doe@example.com or phone (555) 123-4567. "
        "Blood pressure 120/80, zip code 60614. "
        "Accessed from IP 192.168.1.10."
    )

    print("Original:")
    print(sample)
    print("\nDetections:")
    for d in detect(sample):
        print(" ", d)

    print("\nRedacted:")
    print(redact(sample))