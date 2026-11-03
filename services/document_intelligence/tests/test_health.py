from document_intelligence.main import app


def test_service_metadata():
    assert app.title == "ReAugmenAI Document Intelligence"
