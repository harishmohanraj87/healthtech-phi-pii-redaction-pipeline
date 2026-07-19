# 📜 Logging & Audit Trail

This directory is responsible for maintaining a secure and detailed record of how data moves through the Privacy & Data Layer.

## 🎯 Purpose
In healthcare and privacy applications, it is critical to know *who* accessed *what* and *when*. The logger tracks every time PHI is redacted (tokenized) and every time it is revealed (de-tokenized/reverse mapped).

## 📂 Files
* `__init__.py`: Initializes the folder as a Python module. (Specific logging scripts will be added here during Week 2/3).

## 🚀 Responsibilities (Member 3)
* Track and log all token generation events.
* Record all reverse-mapping (re-identification) requests.
* Ensure logs do not accidentally contain raw PHI/PII (log the actions and tokens, never the sensitive data itself).
* Monitor metrics and performance latency for the audit trail.