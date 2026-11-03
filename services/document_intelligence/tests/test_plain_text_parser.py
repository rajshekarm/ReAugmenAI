import pytest

from document_intelligence.infrastructure.parsers.plain_text import PlainTextParser


def test_parser_creates_one_page_per_form_feed():
    pages = PlainTextParser().parse(
        b"First page\fSecond page",
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
    )

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[0].text == "First page"
    assert pages[1].page_number == 2
    assert pages[1].text == "Second page"


def test_parser_attaches_processing_identity_to_each_page():
    pages = PlainTextParser().parse(
        b"Content",
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
    )

    assert pages[0].document_id == "doc-1"
    assert pages[0].version_id == "version-1"
    assert pages[0].processing_run_id == "run-1"


def test_parser_returns_an_empty_first_page_for_empty_content():
    pages = PlainTextParser().parse(
        b"",
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
    )

    assert len(pages) == 1
    assert pages[0].text == ""


def test_parser_rejects_invalid_utf8():
    with pytest.raises(UnicodeDecodeError):
        PlainTextParser().parse(
            b"\xff\xfe",
            document_id="doc-1",
            version_id="version-1",
            processing_run_id="run-1",
        )
