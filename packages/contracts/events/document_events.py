"""Minimal event contracts; evolve these additively and version explicitly."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DocumentAccepted(BaseModel):
    """Published after an immutable document version is accepted."""

    event_type: Literal["document.accepted"] = "document.accepted"
    event_version: str = "1"
    document_id: str
    version_id: str
    tenant_id: str
    occurred_at: datetime
    content_sha256: str = Field(min_length=1)
