import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import DocumentStatus


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    filename: str
    size_bytes: int
    status: DocumentStatus
    page_count: int | None
    chunk_count: int
    error_message: str | None
    created_at: datetime


class SourceOut(BaseModel):
    document_id: uuid.UUID
    filename: str
    page_number: int
    content: str
    similarity: float
    citation: str


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    document_ids: list[uuid.UUID] = Field(default_factory=list, max_length=50)


class AskResponse(BaseModel):
    answer: str
    status: str
    sources: list[SourceOut]
    model: str
    retrieval_ms: int
    generation_ms: int


class ProviderCheck(BaseModel):
    valid: bool
    model: str
    message: str

