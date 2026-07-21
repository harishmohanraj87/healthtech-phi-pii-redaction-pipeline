from fastapi import APIRouter
from app.schemas.redaction import RedactionRequest, RedactionResponse
from app.services.pipeline import RedactionPipeline

router = APIRouter()

pipeline = RedactionPipeline()


@router.get("/")
def root():
    return {
        "status": "running",
        "service": "PHI/PII Redaction Pipeline"
    }


@router.get("/health")
def health():
    return {
        "status": "healthy"
    }


@router.post("/redact", response_model=RedactionResponse)
def redact(request: RedactionRequest):
    result = pipeline.process(request.text)
    return result