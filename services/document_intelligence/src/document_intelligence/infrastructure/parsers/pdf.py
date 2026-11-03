"""Native PDF parser backed by PyMuPDF."""

import fitz

from document_intelligence.domain.contracts import DocumentPage


class PdfParser:
    """Extract native text and page dimensions from a PDF document."""

    name = "pdf-pymupdf"
    version = "0.1.0"

    def parse(
        self,
        content: bytes,
        *,
        document_id: str,
        version_id: str,
        processing_run_id: str,
    ) -> tuple[DocumentPage, ...]:
        try:
            pdf = fitz.open(stream=content, filetype="pdf")
        except (fitz.FileDataError, ValueError) as exc:
            raise ValueError("Invalid PDF document") from exc

        try:
            return tuple(
                DocumentPage(
                    document_id=document_id,
                    version_id=version_id,
                    processing_run_id=processing_run_id,
                    page_number=page_number,
                    text=page.get_text("text"),
                    width=page.rect.width,
                    height=page.rect.height,
                )
                for page_number, page in enumerate(pdf, start=1)
            )
        finally:
            pdf.close()
