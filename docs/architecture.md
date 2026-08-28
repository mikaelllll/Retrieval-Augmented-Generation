# Architecture

## Goals

RAG Explorer demonstrates a realistic service boundary while remaining small enough for a two-core Codespace. Durable state belongs in PostgreSQL, transient coordination belongs in Redis, expensive ingestion happens outside HTTP requests, and the language model receives curated evidence rather than database access.

## Components

| Component | Responsibility |
|---|---|
| React + TypeScript | Upload, provider connection, document state, chat, citations, and pipeline feedback |
| Nginx | Static frontend, same-origin `/api` proxy, upload limit, and security headers |
| FastAPI | Validation, workspace isolation, retrieval orchestration, and Gemini requests |
| Celery | Retryable PDF extraction, chunking, and embedding jobs |
| Redis | Celery broker/result backend and bounded transient storage |
| PostgreSQL + pgvector | Documents, chunks, metadata, and cosine vector search |
| FastEmbed + MiniLM | CPU-focused local 384-dimensional ONNX embeddings |
| Gemini | Natural-language synthesis from retrieved evidence |

## Why these boundaries?

- API replicas remain stateless; they can scale independently.
- PDF processing does not consume an HTTP worker or risk request timeouts.
- `task_acks_late` and worker prefetch of one reduce job loss and unfair distribution.
- Original files and permanent metadata are not stored in Redis.
- Provider credentials are request-scoped, never durable application state.
- One Compose project provides reproducibility; each component remains replaceable.

## Scaling path

For production, use object storage for PDFs, managed PostgreSQL/Redis, Alembic migrations, authenticated organizations instead of anonymous workspace IDs, autoscaled worker queues, encrypted secret storage, centralized logs/traces, malware scanning, OCR, and provider-side data controls.
