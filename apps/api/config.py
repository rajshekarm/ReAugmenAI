import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://reaugmen:local@localhost:5432/reaugmen")
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "local-minio-admin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "change-me-minio")
    s3_bucket: str = os.getenv("S3_BUCKET", "reaugmen-originals")
    api_key: str = os.getenv("INGEST_API_KEY", "change-me-local-only")
    tenant_id: str = os.getenv("INGEST_TENANT_ID", "demo-tenant")
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", "26214400"))

settings = Settings()
