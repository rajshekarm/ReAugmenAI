from ingestion.main import app


def test_ingestion_app_metadata():
    assert app.title == "ReAugmenAI Ingestion Service"
