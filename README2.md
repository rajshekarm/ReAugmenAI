# ReAugmenAI

**Enterprise Document Intelligence & Retrieval-Augmented AI Platform**

ReAugmenAI is an ingestion-first platform for turning enterprise documents into traceable, permission-aware knowledge. The planned system combines document ingestion, OCR and layout analysis, content preparation, embeddings, hybrid search, and grounded AI answers. Structured extraction is an additional capability for operational data workflows.

> **Project status:** Early development starter. The current repository includes a functional **development-oriented ingestion API**. OCR, knowledge processing, embeddings, retrieval, RAG answering, and production-grade security controls are **not yet implemented**.

## Design principles

- **Clear service boundaries:** Each capability has an explicit contract and can be independently scaled or deployed when needed. The initial implementation is not a fully deployed microservices system.
- **Source provenance:** Track source document, immutable version, hashes, extraction run, page/region, derived chunks, model and index versions, and answer citations.
- **Security by design:** Authenticate requests, enforce tenant and document permissions, protect sensitive data, and audit important events. Apply access control throughout ingestion, indexing, retrieval, and source downloads.
- **Reliability:** Favor idempotent processing, durable storage, event delivery, retries, failure isolation, and lifecycle reconciliation.
- **Measurable quality:** Evaluate parsing fidelity, retrieval quality, grounded answers, latency, and operational reliability.

## Target core services

These are **logical services**, not a promise of eight separate running microservices today.

| Service | Responsibilities | Candidate technologies |
| --- | --- | --- |
| **1. Ingestion** | Authenticate uploads, validate files, hash, deduplicate, version, store originals, record metadata, emit processing events | FastAPI, PostgreSQL, S3/MinIO, SQLAlchemy |
| **2. Document Intelligence** | Parse native PDFs; OCR scans; detect reading order, tables, charts, formulas, and source locations | PyMuPDF, Docling, PaddleOCR, OpenCV |
| **3. Knowledge Processing** | Normalize extracted elements, preserve headings and provenance, chunk content, enrich metadata | Python, Pydantic, Docling HybridChunker |
| **4. Embedding & Indexing** | Generate embeddings, build vector/lexical indexes, manage re-embedding, updates and deletions | BGE models, OpenSearch or pgvector; optional visual embeddings |
| **5. Retrieval & Search** | Authorized hybrid retrieval, metadata filters, reranking, retrieve evidence and source references | OpenSearch, reranking models, FastAPI |
| **6. RAG Orchestration** | Assemble evidence, call an LLM/VLM, produce answers with citations, handle abstention | FastAPI, optional LangGraph, locally hosted or API-based models |
| **7. Security & Governance** | Identity, document ACLs, policy enforcement, encryption, audit, retention and deletion | OIDC/Keycloak, OPA, Vault/KMS, PostgreSQL |
| **8. Evaluation & Observability** | Pipeline traces, errors, metrics, test datasets, retrieval/answer evaluations | OpenTelemetry, Prometheus, Grafana, Ragas/DeepEval |

**Optional ninth capability:** Structured Extraction & Validation for typed fields, table records, contracts, financial data, business rules, and human review.

Security and observability are **cross-cutting controls**, not downstream optional stages.

## Intended processing flow

1. **Accept document:** verify caller, inspect file, assign stable identifiers, preserve original, record a new immutable version.
2. **Extract content:** route native text to a parser and scanned pages to OCR; preserve layout and source page locations.
3. **Prepare knowledge:** normalize content and create provenance-linked chunks.
4. **Generate embeddings and indexes:** store vectors, lexical content, metadata, permission references, and model versions.
5. **Retrieve:** check user authorization, run hybrid search and reranking, and return relevant evidence.
6. **Answer:** let an LLM reason over retrieved evidence and return verifiable source citations.
7. **Maintain:** propagate document updates, revocation, deletion and reindexing to all derived assets.

Embedding generation belongs in **knowledge indexing**, not the upload request path. Charts and images may require separate visual retrieval or extraction; text embeddings alone do not capture every chart value.

## What is implemented in the starter

- FastAPI endpoints for document upload, list, detail and original download.
- PostgreSQL-backed document metadata and versions using SQLAlchemy.
- MinIO / S3-compatible original-file storage.
- Streaming upload with configured size limits, SHA-256 hashing, and basic signature checks.
- A fixed development tenant derived from API-key configuration, not client-provided tenant input.
- Transactional outbox **records** (the event publisher/consumer is not implemented).
- Request IDs, basic audit records, health endpoint, and initial API tests.
- Placeholder directories for future document intelligence, knowledge indexing, and RAG modules.

### Current repository structure

```text
ReAugmenAI-starter/
├── apps/
│   ├── api/                    # Current ingestion API
│   ├── document_intelligence/  # Placeholder
│   ├── knowledge_indexing/     # Placeholder
│   └── rag/                    # Placeholder
├── tests/
├── .env.example
├── compose.yaml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Quick start

**Prerequisites:** Docker and Docker Compose.

```bash
cp .env.example .env
```

Edit `.env` to replace development secrets **before use**. Then run:

```bash
docker compose up --build -d
```

API documentation: **http://localhost:8000/docs**

Health check:

```bash
curl http://localhost:8000/health
```

Upload a PDF (the API key below is the default development example; use the value from your `.env`):

```bash
curl -X POST http://localhost:8000/v1/documents \
  -H 'X-API-Key: change-me-local-only' \
  -F 'file=@example.pdf'
```

List uploaded documents:

```bash
curl -H 'X-API-Key: change-me-local-only' \
  http://localhost:8000/v1/documents
```

Run the supplied tests (requires Python development dependencies and any services the tests depend on):

```bash
pip install -e '.[dev]'
pytest -q
```

> The starter has not been certified through a full production integration/security test. The Docker Compose configuration and example credentials are strictly for local development.

## Current API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health status |
| `POST` | `/v1/documents` | Upload and register document |
| `GET` | `/v1/documents` | List documents for configured tenant |
| `GET` | `/v1/documents/{document_id}` | Get document metadata |
| `GET` | `/v1/documents/{document_id}/download` | Download original document |

Future APIs will be documented when implemented; do not assume extraction, embedding, search or RAG endpoints already exist.

## Production hardening roadmap

**Priority 1 — Secure and reliable ingestion:** enterprise OIDC/service identity, fine-grained ACLs, malware scanning/quarantine, parser sandboxing, migration tooling, secrets/KMS/TLS, storage/DB reconciliation, durable outbox publisher and consumers, idempotency, retries/DLQ, audit retention, and integration tests.

**Priority 2 — Document Intelligence:** native and scanned PDF extraction, layout regions, tables, visual assets, extraction metadata, page-level evidence and validation benchmarks.

**Priority 3 — Searchable knowledge:** provenance-aware chunking, embeddings, lexical indexing, ACL propagation, hybrid retrieval, reranking, update/delete synchronization and retrieval evaluation.

**Priority 4 — Answering and automation:** RAG answers with citations and abstention, visual evidence retrieval, optional typed structured extraction, human approval workflows, and comprehensive model evaluation.

## Explicit non-goals for the current starter

The existing project is **not** a bank-certified system, a deployed enterprise RAG platform, a complete OCR engine, an embedding service, or a production microservice fleet. Its purpose is to establish the ingestion foundation and clear contracts for subsequent capabilities.

## Project name

**ReAugmenAI** — *Enterprise Knowledge. Augmented Intelligence.*
