# Regex Detector — PHI/PII Detection Engine

**Owner:** Yash Kulkarni (Detection Engine Lead)
**File:** `detectors/regex_detector.py`
**Tests:** `tests/test_regex_detector.py`

## What it does

Scans raw clinical text and detects PHI/PII entities using regex patterns.
Returns a list of `Detection` objects (type, matched text, character span),
and can optionally redact the text by replacing matches with `[ENTITY_TYPE]`
placeholders.

## Entities detected (9 total)

| Entity      | Example                          |
|-------------|-----------------------------------|
| PHONE       | (555) 123-4567                    |
| EMAIL       | john.doe@example.com              |
| DATE        | 04/12/2025, January 5, 2026       |
| MRN         | MRN: 1029384756                   |
| SSN         | 123-45-6789                       |
| ZIP         | zip code 60614                    |
| IP_ADDRESS  | 192.168.1.10                      |
| ADDRESS     | 742 Evergreen Terrace             |
| AGE         | 65 years old, Age: 42             |

## Usage

```python
from detectors.regex_detector import detect, redact

text = "Patient MRN: 1029384756, contacted on 04/12/2025."

detections = detect(text)   # list[Detection]
redacted = redact(text)     # "Patient [MRN], contacted on [DATE]."
```

## Design notes

- **Overlap resolution**: if two patterns match overlapping text, the
  longer match wins and the shorter one is dropped. Prevents double
  redaction or corrupted output.
- **Context-gated patterns**: ZIP and AGE require a nearby keyword
  ("zip", "years old", "age") so we don't flag every stray number in
  a note as PII. This was a key fix after early testing showed
  false positives on things like room numbers and blood pressure
  readings (120/80 was briefly caught by the DATE pattern).
- Known limitation: ADDRESS uses a fixed suffix list (St, Ave, Terrace,
  etc.) — non-US or unusual address formats may be missed. This is a
  regex-only layer; NLP-based detection (Presidio/spaCy, Week 2) will
  catch what regex can't.

## Test coverage

30 tests total across Day 1–3, covering:
- Correct detection of each entity type
- Multiple formats per entity (e.g. 3 date formats, 3 age formats)
- False-positive guards (vitals, room numbers, random capitalized text)
- Full end-to-end clinical note redaction

Run tests:
```bash
pytest tests/test_regex_detector.py -v
```