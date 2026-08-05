from pydantic import BaseModel


class RestoreRequest(BaseModel):
    text: str


class RestoreResponse(BaseModel):
    restored_text: str