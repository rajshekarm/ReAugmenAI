from ingestion.main import ALLOWED, app, serialize_document


def test_ingestion_app_metadata():
    assert app.title == "ReAugmenAI Ingestion Service"


def test_supported_signatures():
    assert ALLOWED[".pdf"][1](b"%PDF-1.7")
    assert not ALLOWED[".pdf"][1](b"NOTPDF")
    assert ALLOWED[".png"][1](b"\x89PNG\r\n\x1a\n")
