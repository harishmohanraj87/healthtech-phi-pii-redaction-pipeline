from pydantic import BaseModel


class RedactionRequest(BaseModel):
    text: str


class RedactionResponse(BaseModel):
    redacted_text: str
    detections: list