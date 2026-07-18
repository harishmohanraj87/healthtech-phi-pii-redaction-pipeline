"""
medical_terms.py
Yash Kulkarni - Detection Engine Lead
Week 3 / Day 8: Expanded medical condition/disease name reference.

Why this is a separate file:
  The original allowlist in nlp_detector.py had ~10 entries, enough to
  prove the "Parkinson Disease" requirement worked, but nowhere near
  enough for real clinical notes. Splitting this into its own data
  module makes it easy to keep growing without cluttering the
  detection logic, and makes the list reusable if Member 1 or Member 3
  ever need it elsewhere in the pipeline.

This list covers common conditions likely to appear in clinical notes
that could otherwise be mistaken for a patient's name by an NLP PERSON
recognizer (eponymous diseases, syndromes named after people, etc.)
plus general disease/condition terms.
"""

from typing import Set

# Eponymous diseases/syndromes (named after a person) — these are the
# highest-risk category for false-positive PERSON detection, since they
# look exactly like a proper noun.
EPONYMOUS_CONDITIONS: Set[str] = {
    "parkinson", "parkinson's", "parkinsons",
    "alzheimer", "alzheimer's", "alzheimers",
    "crohn", "crohn's", "crohns",
    "hodgkin", "hodgkin's", "hodgkins",
    "graves", "graves'",
    "addison", "addison's",
    "huntington", "huntington's",
    "tourette", "tourette's",
    "asperger", "asperger's",
    "down", "down's",  # Down Syndrome
    "cushing", "cushing's",
    "raynaud", "raynaud's",
    "sjogren", "sjogren's",
    "guillain-barre", "guillain barre",
    "bell's", "bells",  # Bell's Palsy
    "kaposi", "kaposi's",
    "wilson's", "wilsons",  # Wilson's disease
    "paget", "paget's",
    "meniere", "meniere's",
    "tay-sachs", "tay sachs",
    "marfan", "marfan's",
    "duchenne",
    "epstein-barr", "epstein barr",
    "lou gehrig", "lou gehrig's",
    "creutzfeldt-jakob", "creutzfeldt jakob",
    "kawasaki",
    "reye's", "reyes",
    "prader-willi", "prader willi",
    "klinefelter", "klinefelter's",
    "turner's", "turners",  # Turner syndrome
    "barrett's", "barretts",  # Barrett's esophagus
}

# General condition/syndrome names — not eponymous, but still risk
# being flagged if they appear capitalized at the start of a sentence
# or in a title-case clinical note header.
GENERAL_CONDITIONS: Set[str] = {
    "down syndrome", "down's syndrome",
    "irritable bowel syndrome",
    "chronic fatigue syndrome",
    "restless leg syndrome",
    "polycystic ovary syndrome",
    "carpal tunnel syndrome",
    "metabolic syndrome",
    "sudden infant death syndrome",
    "acquired immunodeficiency syndrome",
    "respiratory distress syndrome",
}

# Combined set used by the detector
MEDICAL_TERM_ALLOWLIST: Set[str] = EPONYMOUS_CONDITIONS | GENERAL_CONDITIONS

# Context words that, when found immediately after a capitalized term,
# suggest it's a medical condition rather than a person's name.
MEDICAL_CONTEXT_WORDS: Set[str] = {
    "disease", "syndrome", "disorder", "diagnosis",
    "palsy", "esophagus", "syndrome,",
}


def is_known_medical_term(text: str) -> bool:
    """Quick lookup: is this exact term (case-insensitive) a known condition?"""
    return text.strip().lower() in MEDICAL_TERM_ALLOWLIST


def contains_medical_term(text: str) -> bool:
    """Does this text contain a known condition as a substring?"""
    lowered = text.strip().lower()
    return any(term in lowered for term in MEDICAL_TERM_ALLOWLIST)
