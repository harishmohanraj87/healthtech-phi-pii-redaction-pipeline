# Detection Engine — PHI/PII Redaction Pipeline

**Owner:** Yash Kulkarni (Detection Engine Lead)

This module is responsible for detecting PHI/PII entities in clinical
text. It has two layers — regex (structured entities) and NLP
(unstructured/free-text entities) — plus a combined interface, an
accuracy evaluation framework, and a performance benchmark.

## Files

| File | Purpose |
|---|---|
| `detectors/regex_detector.py` | Structured entity detection via regex |
| `detectors/nlp_detector.py` | Free-text entity detection via Presidio + spaCy |
| `detectors/medical_terms.py` | Reference list of 75 medical conditions used to prevent disease names being redacted as patient names |
| `detectors/combined_detector.py` | Unified interface merging both layers |
| `detectors/accuracy_eval.py` | Precision/Recall/F1 measurement against a labeled dataset |
| `detectors/benchmark.py` | Performance benchmark on large clinical notes |
| `requirements.txt` | Python dependencies |

## Entities detected

**Regex layer (9 types):** PHONE, EMAIL, DATE, MRN, SSN, ZIP, IP_ADDRESS, ADDRESS, AGE

**NLP layer (4 types):** PERSON, LOCATION, ORGANIZATION, MRN (via custom recognizer)

## Quick start

```python
from detectors.combined_detector import CombinedDetector

detector = CombinedDetector()

text = "Patient MRN: 1029384756, diagnosed with Parkinson Disease, contacted on 04/12/2025."

detections = detector.detect(text)   # list[CombinedDetection]
redacted = detector.redact(text)     # "Patient [MRN], diagnosed with Parkinson Disease, contacted on [DATE]."
```

The regex layer works with zero extra installs (standard library only).
The NLP layer requires Presidio + spaCy:

```bash
pip install -r requirements.txt --break-system-packages
python -m spacy download en_core_web_lg
```

If Presidio isn't installed, `CombinedDetector` automatically falls
back to regex-only mode — it won't crash, it just won't catch
free-text entities like patient names.

## Critical design decision: protecting medical terms

Early testing showed Presidio's PERSON recognizer would flag disease
names like "Parkinson Disease" as if they were a patient's name,
because capitalized eponymous conditions look like proper nouns to
the underlying NER model.

This is fixed two ways:
1. `medical_terms.py` — a 75-entry allowlist of known conditions,
   checked directly against any PERSON match.
2. A custom Presidio `MEDICAL_TERM` recognizer that cross-checks
   overlapping spans as a second layer of protection.

Both layers are tested in `tests/test_medical_terms.py` and
`tests/test_nlp_detector.py`.

## Accuracy

Measured against a 15-case labeled dataset (`accuracy_eval.py`):

```
Precision: 100.0%
Recall:    100.0%
F1 Score:  100.0%
```

Run it yourself: `python3 detectors/accuracy_eval.py`

`tests/test_accuracy_eval.py` enforces a 95% minimum threshold on all
three metrics as a regression guard.

## Performance

On a realistic 17.5KB, 20-visit clinical document
(`detectors/benchmark.py`):

```
Time taken:  ~10 ms
Throughput:  ~1.8 million characters/second
```

Run it yourself: `python3 -m detectors.benchmark`

## Known limitations

- ADDRESS regex uses a fixed suffix list (St, Ave, Terrace, etc.) —
  unusual or non-US address formats may be missed.
- The medical term allowlist, while covering 75 conditions, is not
  exhaustive. New eponymous diseases encountered during testing should
  be added to `medical_terms.py`.
- NLP layer requires Presidio/spaCy to be installed locally; it is not
  run in this environment's automated tests for that reason (those
  tests target the allowlist logic only, which doesn't need Presidio).

## Test coverage

71 tests total across all modules:
- 30 — regex_detector (all entity types + false-positive guards)
- 9 — nlp_detector (medical term allowlist core cases)
- 11 — medical_terms (expanded allowlist coverage)
- 7 — combined_detector (cross-layer overlap resolution)
- 7 — edge_cases (large documents, dense entity clusters, multi-visit notes)
- 7 — accuracy_eval (precision/recall/F1 threshold enforcement, self-validated)

Run everything:
```bash
pytest tests/ -v
```
