"""Ingestion service entry point."""

import hashlib
import json
import re
import tempfile
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ingestion import models
from ingestion.config import settings
from ingestion.db import Base, engine, get_db
from ingestion.security import current_tenant
from ingestion.storage import Storage

ALLOWED = {
    ".pdf": ("application/pdf", lambda b: b.startswith(b"%PDF-")),
    ".png": ("image/png", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    ".jpg": ("image/jpeg", lambda b: b.startswith(b"\xff\xd8\xff")),
    ".jpeg": ("image/jpeg", lambda b: b.startswith(b"\xff\xd8\xff")),
    ".docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", lambda b: b.startswith(b"PK\x03\x04")),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    Storage().ensure_bucket()
    yield


app = FastAPI(title="ReAugmenAI Ingestion Service", version="0.1.0", lifespan=lifespan)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ingestion"}


def serialize_document(doc, ver):
    return {"document_id": doc.id, "version_id": ver.id, "version": ver.version_number,
            "filename": doc.filename, "content_type": ver.content_type,
            "size_bytes": ver.size_bytes, "sha256": ver.sha256, "status": ver.status,
            "created_at": ver.created_at.isoformat()}


@app.post("/v1/documents", status_code=201)
async def upload_document(file: UploadFile = File(...), tenant: str = Depends(current_tenant), db: Session = Depends(get_db)):
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in ALLOWED or not re.fullmatch(r"[a-zA-Z0-9_.() -]{1,255}", filename):
        raise HTTPException(400, "Invalid filename or unsupported file extension")
    expected_type, signature_matches = ALLOWED[suffix]
    sha = hashlib.sha256()
    size = 0
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="reaug-upload-", delete=False) as tmp:
            temp_path = Path(tmp.name)
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_bytes:
                    raise HTTPException(413, "File exceeds upload size limit")
                sha.update(chunk)
                tmp.write(chunk)
        with temp_path.open("rb") as stream:
            header = stream.read(16)
        if not size or not signature_matches(header):
            raise HTTPException(400, "File signature does not match extension")
        digest = sha.hexdigest()
        doc = models.Document(id=str(uuid.uuid4()), tenant_id=tenant, filename=filename)
        ver = models.DocumentVersion(id=str(uuid.uuid4()), document_id=doc.id, version_number=1, sha256=digest,
            content_type=expected_type, size_bytes=size,
            object_key=f"{tenant}/sha256/{digest[:2]}/{digest}", status="accepted")
        Storage().upload_file(temp_path, ver.object_key, expected_type)
        db.add(doc)
        db.add(ver)
        db.add(models.OutboxEvent(aggregate_id=ver.id, event_type="document.accepted",
            payload_json=json.dumps({"document_id": doc.id, "version_id": ver.id, "tenant_id": tenant})))
        db.add(models.AuditEvent(tenant_id=tenant, action="document.accepted", resource_id=doc.id))
        db.commit()
        return serialize_document(doc, ver)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(503, "Upload could not be completed")
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        await file.close()


@app.get("/v1/documents")
def list_documents(tenant: str = Depends(current_tenant), db: Session = Depends(get_db)):
    rows = db.execute(select(models.Document, models.DocumentVersion).join(
        models.DocumentVersion, models.Document.id == models.DocumentVersion.document_id
    ).where(models.Document.tenant_id == tenant).order_by(models.Document.created_at.desc()).limit(100)).all()
    return [serialize_document(doc, ver) for doc, ver in rows]


@app.get("/v1/documents/{document_id}")
def get_document(document_id: str, tenant: str = Depends(current_tenant), db: Session = Depends(get_db)):
    row = db.execute(select(models.Document, models.DocumentVersion).join(
        models.DocumentVersion, models.Document.id == models.DocumentVersion.document_id
    ).where(models.Document.id == document_id, models.Document.tenant_id == tenant)).first()
    if not row:
        raise HTTPException(404, "Document not found")
    return serialize_document(*row)


@app.get("/v1/documents/{document_id}/download")
def download_document(document_id: str, tenant: str = Depends(current_tenant), db: Session = Depends(get_db)):
    row = db.execute(select(models.Document, models.DocumentVersion).join(
        models.DocumentVersion, models.Document.id == models.DocumentVersion.document_id
    ).where(models.Document.id == document_id, models.Document.tenant_id == tenant)).first()
    if not row:
        raise HTTPException(404, "Document not found")
    doc, ver = row
    body = Storage().download_stream(ver.object_key)

    def chunks():
        try:
            for part in body.iter_chunks(chunk_size=65536):
                if part:
                    yield part
        finally:
            body.close()

    return StreamingResponse(chunks(), media_type=ver.content_type,
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'})
