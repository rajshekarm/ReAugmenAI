import secrets

from fastapi import Header, HTTPException, status

from ingestion.config import settings


def current_tenant(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return settings.tenant_id
