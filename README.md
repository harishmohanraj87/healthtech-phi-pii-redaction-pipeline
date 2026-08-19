# 🏥 HealthTech – Automated PHI/PII Redaction Pipeline for LLMs

> A secure FastAPI-based PHI/PII redaction pipeline that detects sensitive information in clinical text and replaces it with secure reversible tokens before the data can be forwarded to external AI/LLM systems.

---

## 📌 Project Overview

Healthcare organizations are increasingly adopting AI-powered clinical assistants and generative AI systems to support documentation and clinical workflows.

However, sending raw clinical text to external AI services can expose sensitive patient information.

This project addresses that problem by providing a security layer between clinical applications and external AI systems.

The pipeline detects PHI/PII using a combination of:

- Rule-based Regex detection
- NLP-based entity recognition
- Microsoft Presidio
- spaCy
- Custom recognizers
- Medical-condition allowlists
- Cross-layer overlap resolution

Detected sensitive values are replaced with secure tokens. The original values are stored in a Redis-based token vault so that authorized restoration can be performed when required.

---

# 👥 Team

| Name | Role | Responsibilities |
|---|---|---|
| **Harish Mohanraj** | Technical Lead & Backend Integration | Project architecture, FastAPI backend, API integration, repository management, testing, documentation, deployment, code reviews |
| **Yash Kulkarni** | NLP Detection Engineer | Microsoft Presidio integration, spaCy-based PHI detection, custom recognizers, allowlist implementation, NLP testing |
| **Surya** | Detection & Validation Engineer | Regex-based PHI/PII detection, validation logic, test development, detector improvements, documentation support |

---

# 🚀 Current MVP Features

### Detection

- Regex-based PHI/PII detection
- NLP-based entity recognition
- Microsoft Presidio integration
- spaCy support
- Combined Regex + NLP detector
- Cross-layer overlap resolution
- Medical-condition allowlist
- Custom MRN recognition

### Privacy Protection

- PHI/PII tokenization
- Secure token generation
- Redis token vault
- Reversible token mapping
- Token restoration
- Audit logging

### API

- FastAPI backend
- `POST /redact`
- `POST /restore`
- `GET /health`
- Interactive Swagger API documentation

### Frontend

- AdminLTE-based security dashboard
- PHI/PII Redaction interface
- Token Restoration interface
- Detection results table
- Processing metrics
- Token display
- Copy/Clear actions
- System and Redis status information

### Testing

- Automated Pytest test suite
- Detector tests
- Regex tests
- NLP tests
- Combined detector tests
- Token vault tests
- Restoration tests
- Performance/benchmark testing

---

# 🏗️ Architecture

```text
                    Clinical Text
                         │
                         ▼
                  ┌─────────────┐
                  │   FastAPI   │
                  │    Proxy    │
                  └──────┬──────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Combined        │
                │ Detector        │
                └────────┬────────┘
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
        Regex Detector       NLP Detector
                │                 │
                └────────┬────────┘
                         │
                         ▼
                 Overlap Resolution
                         │
                         ▼
                  Token Vault
                         │
                         ▼
                       Redis
                         │
                         ▼
                 Secure Tokens
                         │
                         ▼
                 Redacted Text
                         │
                         ▼
               External LLM / AI
                 (Future Phase)
