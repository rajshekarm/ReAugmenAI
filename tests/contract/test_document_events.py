from datetime import datetime, timezone

from packages.contracts.events.document_events import DocumentAccepted


def test_document_accepted_contract_is_versioned():
    event = DocumentAccepted(
        document_id="doc-1",
        version_id="version-1",
        tenant_id="tenant-1",
        occurred_at=datetime.now(timezone.utc),
        content_sha256="abc123",
    )
    assert event.event_type == "document.accepted"
    assert event.event_version == "1"
