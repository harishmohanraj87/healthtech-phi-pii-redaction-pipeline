# 🏥 HealthTech – Automated PHI/PII Redaction Pipeline for LLMs

> A secure AI-powered proxy service that detects and anonymizes Protected Health Information (PHI) and Personally Identifiable Information (PII) before clinical text is sent to Large Language Models (LLMs).

---

## 📌 Project Overview

Healthcare organizations are increasingly adopting AI-powered clinical assistants and generative AI models to automate documentation. However, sending raw patient conversations to external AI services can expose sensitive patient information and violate privacy regulations such as **HIPAA** and **PIPEDA**.

This project aims to build a secure **PHI/PII Redaction Pipeline** that intercepts clinical text, detects sensitive identifiers using Natural Language Processing (NLP), anonymizes them, and forwards only the sanitized content to an LLM.

The objective is to enable AI-assisted healthcare workflows while preserving patient privacy and maintaining regulatory compliance.

---

## 🎯 Objectives

* Detect Protected Health Information (PHI)
* Detect Personally Identifiable Information (PII)
* Redact sensitive information before LLM processing
* Preserve clinical context for accurate AI responses
* Provide audit logging for compliance and traceability
* Build a modular and extensible redaction pipeline

## 👥 Team

| Name                | Role                                 | Responsibilities                                                                                                                |
| ------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| **Harish Mohanraj** | Technical Lead & Backend Integration | Project architecture, FastAPI backend, API integration, repository management, testing, documentation, deployment, code reviews |
| **Yash Kulkarni**   | NLP Detection Engineer               | Microsoft Presidio integration, spaCy-based PHI detection, custom recognizers, allowlist implementation, NLP testing            |
| **Surya**           | Detection & Validation Engineer      | Regex-based PHI/PII detection, validation logic, test development, detector improvements, documentation support                 |

## 🚀 Current Features

* Regex-based PHI detection
* NLP-based entity recognition
* Microsoft Presidio integration
* spaCy NLP support
* Medical-condition allowlist
* Custom MRN recognizer
* PHI anonymization
* Audit logging
* Unit testing
* Modular project structure

---

## 🛠️ Technology Stack

### Backend

* Python
* FastAPI

### NLP

* Microsoft Presidio
* spaCy
* Regular Expressions (Regex)

### AI Integration

* OpenAI API *(planned)*
* Google Gemini *(planned)*

### Testing

* Pytest

### Deployment

* Docker *(planned)*

---

## 📂 Project Structure

```text
healthtech-phi-pii-redaction-pipeline/

├── app/
├── detectors/
├── anonymizer/
├── tests/
├── docs/
├── sample_data/
├── README.md
├── requirements.txt
└── LICENSE
```

---

## 🔄 Project Workflow

```text
Clinical Transcript
        │
        ▼
Regex Detection
        │
        ▼
NLP Detection
        │
        ▼
PHI / PII Recognition
        │
        ▼
Anonymization
        │
        ▼
Audit Logging
        │
        ▼
Sanitized Text
        │
        ▼
Large Language Model
```

---

## 🔒 PHI/PII Detection

The pipeline is designed to detect identifiers including:

* Patient Names
* Dates
* Phone Numbers
* Email Addresses
* Medical Record Numbers (MRN)
* Addresses
* Social Security Numbers
* IP Addresses
* URLs
* Additional HIPAA Safe Harbor identifiers

---

## 🧠 Smart Detection

Unlike simple regex filters, the project combines NLP and rule-based detection to improve accuracy.

Current improvements include:

* Custom Presidio recognizers
* Medical-condition allowlist to prevent diseases from being mistaken for patient names
* Overlap handling between recognizers
* Context-aware entity detection

---

## ✅ Testing

Current project status:

* 39+ automated tests passing
* Allowlist validation tests
* Entity overlap tests
* Regex validation tests
* Detector validation tests

---

## 📖 Documentation

Additional documentation can be found in the `docs/` and `detectors/` directories.

Topics include:

* Entity detection
* Recognizers
* Project architecture
* Usage
* Known limitations

---

## 🚧 Current Development Status

### Completed

* Project setup
* Regex detector
* NLP detector
* Medical-condition allowlist
* MRN recognizer
* Unit testing
* Documentation

### In Progress

* FastAPI proxy
* LLM integration
* Audit dashboard
* API endpoints
* Clinical note generation

### Planned

* Production deployment
* Docker support
* Authentication
* Role-Based Access Control (RBAC)
* OCR support
* PDF document processing
* FHIR/HL7 integration
* Multi-language PHI detection

---

## 🤝 Contributing

This project is currently being developed as part of a collaborative HealthTech internship. Contributions and improvements are welcome through pull requests and issue discussions.

---

## 📄 License

This project is intended for educational and internship purposes. The appropriate open-source license will be added as development progresses.

---

## ⭐ Future Roadmap

* Complete FastAPI proxy service
* Integrate external LLM APIs
* Add healthcare compliance dashboard
* Improve PHI detection accuracy
* Support all HIPAA Safe Harbor identifiers
* Add performance benchmarking
* Containerize the application using Docker
* Prepare for production deployment
