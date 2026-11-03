"""Versioned contracts shared by document-intelligence pipeline stages."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


ProcessingStatus = Literal["queued", "running", "completed", "failed"]
ElementType = Literal["heading", "paragraph", "table", "figure", "metadata", "unknown"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BoundingBox(BaseModel):
    """Coordinates for an element on a page."""

    x0: float = Field(ge=0)
    y0: float = Field(ge=0)
    x1: float = Field(ge=0)
    y1: float = Field(ge=0)


class Provenance(BaseModel):
    """Source location and processing metadata for a derived element."""

    document_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    processing_run_id: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    element_id: str = Field(min_length=1)
    extraction_method: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    model_version: str | None = None
    bounding_box: BoundingBox | None = None


class DocumentPage(BaseModel):
    """Page-level content produced by a parser or OCR adapter."""

    document_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    processing_run_id: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    text: str = ""
    width: float | None = Field(default=None, ge=0)
    height: float | None = Field(default=None, ge=0)


class DocumentElement(BaseModel):
    """A meaningful element extracted from a document page."""

    element_id: str = Field(min_length=1)
    element_type: ElementType
    text: str = ""
    confidence: float = Field(ge=0, le=1)
    provenance: Provenance


class ProcessingError(BaseModel):
    """Safe, serializable representation of a processing failure."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    retryable: bool = False
    component: str = Field(min_length=1)


class DocumentArtifact(BaseModel):
    """Complete output contract passed to downstream knowledge processing."""

    document_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    processing_run_id: str = Field(min_length=1)
    status: Literal["completed"] = "completed"
    parser_name: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    pages: list[DocumentPage] = Field(default_factory=list)
    elements: list[DocumentElement] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class ProcessingEvent(BaseModel):
    """Base fields shared by all processing events."""

    event_version: str = "1"
    document_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    processing_run_id: str = Field(min_length=1)
    occurred_at: datetime = Field(default_factory=utc_now)


class DocumentProcessingStarted(ProcessingEvent):
    event_type: Literal["document.processing.started"] = "document.processing.started"
    status: Literal["running"] = "running"


class DocumentProcessed(ProcessingEvent):
    event_type: Literal["document.processed"] = "document.processed"
    status: Literal["completed"] = "completed"
    artifact: DocumentArtifact


class DocumentProcessingFailed(ProcessingEvent):
    event_type: Literal["document.processing.failed"] = "document.processing.failed"
    status: Literal["failed"] = "failed"
    error: ProcessingError
