from fastapi import FastAPI

app = FastAPI(
    title="HealthTech PHI/PII Redaction Pipeline",
    version="0.1.0"
)

@app.get("/")
def health():
    return {
        "status": "running",
        "service": "PHI/PII Redaction Pipeline"
    }