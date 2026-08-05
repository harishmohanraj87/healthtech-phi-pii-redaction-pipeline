from fastapi import APIRouter

from app.schemas.redaction import RedactionRequest, RedactionResponse
from app.schemas.restore import RestoreRequest, RestoreResponse
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
    """
    Detect PHI/PII entities and replace them with secure tokens.
    """
    return pipeline.process(request.text)


@router.post("/restore", response_model=RestoreResponse)
def restore(request: RestoreRequest):
    """
    Restore secure tokens back to their original PHI values.
    """
    restored_text = pipeline.restore(request.text)

    return RestoreResponse(
        restored_text=restored_text
    )