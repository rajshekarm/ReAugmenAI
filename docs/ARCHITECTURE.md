# Architecture

ReAugmenAI is organized around document-version ownership, independently deployable
services, and explicit versioned contracts.

## Platform architecture

```mermaid
flowchart LR
    U[Users and enterprise applications]
    SRC[Uploads and approved enterprise sources]

    subgraph SERVICES[Independent ReAugmenAI services]
        ING[Ingestion\nvalidate • hash • store • version]
        DI[Document Intelligence\nparse • OCR • layout • provenance]
        KP[Knowledge Processing\nnormalize • chunk • enrich]
        EI[Embedding and Indexing\nembed • index • update]
        RET[Retrieval\nfilter • hybrid search • rerank]
        RAG[RAG Orchestration\ncontext • model • citations]
        SE[Structured Extraction\nfields • tables • validation]
    end

    subgraph SHARED[Shared platform packages]
        CONTRACTS[Versioned contracts\nevents • schemas]
        COMMON[Common utilities\nerrors • logging • telemetry]
    end

    subgraph DATA[Data and platform infrastructure]
        OBJ[(S3 / MinIO\noriginals and artifacts)]
        DB[(PostgreSQL\nmetadata and state)]
        BUS[(Event bus / task queue)]
        OBS[Observability\nmetrics • traces • logs]
    end

    SRC --> ING
    ING --> OBJ
    ING --> DB
    ING -->|document.accepted| BUS
    BUS --> DI
    DI --> OBJ
    DI -->|document.processed| BUS
    BUS --> KP
    KP --> EI
    EI --> RET

    U --> RET
    RET --> RAG
    RAG --> U
    DI --> SE
    SE --> U

    CONTRACTS -. shared by .-> ING
    CONTRACTS -. shared by .-> DI
    CONTRACTS -. shared by .-> KP
    CONTRACTS -. shared by .-> EI
    CONTRACTS -. shared by .-> RET
    CONTRACTS -. shared by .-> RAG
    CONTRACTS -. shared by .-> SE
    COMMON -. cross-cutting .-> SERVICES
    SERVICES -. telemetry .-> OBS
```

## Document preparation flow

```mermaid
flowchart LR
    A[Source document] --> B[Ingestion]
    B --> C[Immutable document version]
    C --> D[Document Intelligence]
    D --> D1[Parsing / OCR]
    D1 --> D2[Layout understanding]
    D2 --> D3[Content and provenance]
    D3 --> E[Knowledge Processing]
    E --> F[Embeddings and indexes]
```

## Question-answering flow

```mermaid
flowchart LR
    Q[User question] --> A[Authorization]
    A --> B[Permission-aware retrieval]
    B --> C[Hybrid search and reranking]
    C --> D[Evidence assembly]
    D --> E[RAG orchestration]
    E --> F[Cited answer]
```

## Structured extraction flow

```mermaid
flowchart LR
    A[Document version] --> B[Document Intelligence]
    B --> C[Structured Extraction]
    C --> D[Schema validation]
    D --> E[Business-rule validation]
    E --> F[Authorized downstream workflow]
```

Original documents remain authoritative. Every derived chunk, embedding, evidence item,
and extracted value must retain tenant, document-version, processing-run, and provenance
identifiers. Security, logging, telemetry, retries, and versioned contracts apply across
all services.
