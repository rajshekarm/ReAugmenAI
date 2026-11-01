from apps.api.main import ALLOWED, serialize_document
from apps.api.models import Document, DocumentVersion

def test_supported_signatures():
    assert ALLOWED[".pdf"][1](b"%PDF-1.7")
    assert not ALLOWED[".pdf"][1](b"NOTPDF")
    assert ALLOWED[".png"][1](b"\x89PNG\r\n\x1a\n")

def test_document_contract():
    d = Document(tenant_id="tenant", filename="example.pdf")
    d.id = "doc1"
    v = DocumentVersion(document_id="doc1", sha256="abc", content_type="application/pdf",
                        size_bytes=10, object_key="tenant/key", status="accepted")
    v.id = "version1"
    v.version_number = 1
    from datetime import datetime, timezone
    v.created_at = datetime.now(timezone.utc)
    result = serialize_document(d, v)
    assert result["document_id"] == "doc1"
    assert result["version_id"] == "version1"
    assert "object_key" not in result
