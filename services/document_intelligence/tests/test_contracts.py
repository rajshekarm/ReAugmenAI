from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from document_intelligence.domain.contracts import (
    BoundingBox,
    DocumentElement,
    DocumentPage,
    DocumentProcessed,
    DocumentProcessingFailed,
    DocumentProcessingStarted,
    ProcessingError,
    Provenance,
)


def provenance() -> Provenance:
    return Provenance(
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
        page_number=1,
        element_id="element-1",
        extraction_method="native-text",
        parser_version="parser-1.0.0",
        bounding_box=BoundingBox(x0=0, y0=0, x1=100, y1=50),
    )


def test_page_and_element_contracts_preserve_provenance():
    page = DocumentPage(
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
        page_number=1,
        text="A source paragraph.",
    )
    element = DocumentElement(
        element_id="element-1",
        element_type="paragraph",
        text="A source paragraph.",
        confidence=0.98,
        provenance=provenance(),
    )

    assert page.page_number == 1
    assert element.provenance.document_id == page.document_id
    assert element.provenance.processing_run_id == page.processing_run_id


def test_processing_events_are_versioned_and_serializable():
    started = DocumentProcessingStarted(
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
    )
    failed = DocumentProcessingFailed(
        document_id="doc-1",
        version_id="version-1",
        processing_run_id="run-1",
        occurred_at=datetime.now(timezone.utc),
        error=ProcessingError(
            code="PARSER_TIMEOUT",
            message="Parser timed out",
            retryable=True,
            component="pdf-parser",
        ),
    )

    assert started.event_type == "document.processing.started"
    assert started.event_version == "1"
    assert failed.status == "failed"
    assert failed.error.retryable is True
    assert failed.model_dump()["error"]["code"] == "PARSER_TIMEOUT"


def test_invalid_contract_values_are_rejected():
    with pytest.raises(ValidationError):
        DocumentPage(
            document_id="doc-1",
            version_id="version-1",
            processing_run_id="run-1",
            page_number=0,
        )

    with pytest.raises(ValidationError):
        DocumentElement(
            element_id="element-1",
            element_type="paragraph",
            confidence=1.5,
            provenance=provenance(),
        )
