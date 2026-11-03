"""Document intelligence service entry point."""

from fastapi import FastAPI

app = FastAPI(title="ReAugmenAI Document Intelligence", version="0.1.0")


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "document-intelligence"}
