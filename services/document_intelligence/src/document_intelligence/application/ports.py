"""Application ports for document-intelligence providers."""

from typing import Protocol

from document_intelligence.domain.contracts import DocumentPage


class DocumentParser(Protocol):
    """Interface implemented by native parsers and OCR-backed parsers."""

    name: str
    version: str

    def parse(
        self,
        content: bytes,
        *,
        document_id: str,
        version_id: str,
        processing_run_id: str,
    ) -> tuple[DocumentPage, ...]: ...
