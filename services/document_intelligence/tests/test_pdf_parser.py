import fitz
import pytest

from document_intelligence.infrastructure.parsers.pdf import PdfParser


def pdf_bytes(*page_text: str) -> bytes:
    document = fitz.open()
    try:
        for text in page_text:
            page = document.new_page(width=300, height=400)
            page.insert_text((40, 60), text)
        return document.tobytes()
    finally:
        document.close()


def test_parser_returns_one_document_page_per_pdf_page():
    pages = PdfParser().parse(
        pdf_bytes("First page", "Second page"),
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
    )

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert "First page" in pages[0].text
    assert pages[1].page_number == 2
    assert "Second page" in pages[1].text


def test_parser_preserves_page_dimensions_and_identity():
    pages = PdfParser().parse(
        pdf_bytes("Content"),
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
    )

    page = pages[0]
    assert page.width == 300
    assert page.height == 400
    assert page.document_id == "doc-1"
    assert page.version_id == "version-1"
    assert page.processing_run_id == "run-1"


def test_parser_rejects_invalid_pdf():
    with pytest.raises(ValueError, match="Invalid PDF document"):
        PdfParser().parse(
            b"not-a-pdf",
            document_id="doc-1",
            version_id="version-1",
            processing_run_id="run-1",
        )
