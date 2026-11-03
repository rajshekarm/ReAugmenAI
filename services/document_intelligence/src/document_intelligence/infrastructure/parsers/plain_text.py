"""Deterministic plain-text page parser."""

from document_intelligence.domain.contracts import DocumentPage


class PlainTextParser:
    """Parse UTF-8 text, using form-feed characters as page boundaries."""

    name = "plain-text"
    version = "0.1.0"

    def parse(
        self,
        content: bytes,
        *,
        document_id: str,
        version_id: str,
        processing_run_id: str,
    ) -> tuple[DocumentPage, ...]:
        text = content.decode("utf-8")
        pages = text.split("\f")
        return tuple(
            DocumentPage(
                document_id=document_id,
                version_id=version_id,
                processing_run_id=processing_run_id,
                page_number=page_number,
                text=page,
            )
            for page_number, page in enumerate(pages, start=1)
        )
