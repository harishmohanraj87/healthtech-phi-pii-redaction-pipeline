# Detection Engine — Architecture Diagram

**Owner:** Yash Kulkarni (Detection Engine Lead)

This diagram shows how raw clinical text flows through the detection
engine to produce redacted output. It covers the regex layer, the NLP
layer, the medical term protection system, and where this component
fits in the overall PHI/PII redaction pipeline.

## Detection Engine Flow

```mermaid
flowchart TD
    A[Raw Clinical Text Input] --> B[Regex Detector]
    A --> C[NLP Detector - Presidio + spaCy]

    B --> B1[PHONE, EMAIL, DATE]
    B --> B2[MRN, SSN, ZIP]
    B --> B3[IP_ADDRESS, ADDRESS, AGE]

    C --> C1[PERSON]
    C --> C2[LOCATION]
    C --> C3[ORGANIZATION]

    C1 --> D{Is it a medical term?}
    D -->|Checked against| E[medical_terms.py<br/>75 conditions allowlist]
    E -->|Yes - e.g. Parkinson Disease| F[Discard - NOT a patient name]
    E -->|No - real name| G[Keep as PERSON detection]

    B1 --> H[Combined Detector]
    B2 --> H
    B3 --> H
    C2 --> H
    C3 --> H
    G --> H

    H --> I[Resolve Overlaps<br/>regex wins over NLP on conflicts]
    I --> J[Deduplicated Detection List]
    J --> K[Redacted Output<br/>entities replaced with placeholders]

    style A fill:#2d3748,stroke:#4299e1,color:#fff
    style K fill:#2d3748,stroke:#48bb78,color:#fff
    style F fill:#742a2a,stroke:#fc8181,color:#fff
    style G fill:#22543d,stroke:#68d391,color:#fff
```

## Where This Fits in the Full Pipeline

```mermaid
flowchart LR
    A[Frontend / API Gateway<br/>Member 1] --> B[Detection Engine<br/>Yash Kulkarni]
    B --> C[Token Vault<br/>Member 3]
    C --> D[Redis Storage<br/>Member 3]
    C --> E[Redacted Output<br/>returned to caller]
    D -.reversible mapping.-> F[Re-identification<br/>authorized access only]

    style B fill:#2b6cb0,stroke:#63b3ed,color:#fff
```

## Test & Evaluation Flow

```mermaid
flowchart TD
    A[Detection Engine Code] --> B[71 Unit Tests<br/>pytest]
    A --> C[accuracy_eval.py<br/>18 labeled cases]
    A --> D[benchmark.py<br/>17.5KB clinical doc]

    B --> E[Pass/Fail per function]
    C --> F[Precision: 100%<br/>Recall: 100%<br/>F1: 100%]
    D --> G[~1.8M chars/sec<br/>~10ms processing time]

    style F fill:#22543d,stroke:#68d391,color:#fff
    style G fill:#22543d,stroke:#68d391,color:#fff
```

## Notes for the report/presentation

- The **medical term protection** step (yellow diamond in diagram 1) is the
  single most important design decision in this module — it's the direct
  fix for the "Parkinson Disease must not be redacted" requirement from
  the team roadmap.
- The **combined detector** merges two independently-built layers (regex
  and NLP) without either one needing to know about the other — this
  keeps the code modular and testable in isolation.
- These diagrams render automatically on GitHub (no external tool
  needed) since GitHub supports Mermaid syntax natively in Markdown
  files.
