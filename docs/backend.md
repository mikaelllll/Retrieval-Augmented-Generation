# Backend

The API is asynchronous FastAPI running on Python 3.12. SQLAlchemy uses an asyncpg pool for request-time database work. CPU-heavy model inference stays in the Celery worker.

Alembic migrations run before the API starts; the worker waits for API readiness so it never races schema initialization.

## Data model

- `documents`: workspace ownership, safe display filename, generated storage path, status, pages, chunk count, and a bounded failure message.
- `chunks`: exact document, page and position, normalized text, token estimate, and a 384-dimensional pgvector value.
- HNSW cosine index: approximate nearest-neighbor search suitable for interactive retrieval.

Deleting a document cascades to chunks and removes its generated file. Every list, retrieval, and deletion query filters on the workspace ID.

## HTTP API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health/live` | Process liveness |
| `GET` | `/health/ready` | PostgreSQL and Redis readiness |
| `GET` | `/api/v1/documents` | Workspace document list |
| `POST` | `/api/v1/documents` | Validate, store, and queue one PDF |
| `DELETE` | `/api/v1/documents/{id}` | Remove an owned document |
| `POST` | `/api/v1/provider/check` | Verify a request-scoped Gemini key |
| `POST` | `/api/v1/chat/ask` | Retrieve evidence and generate an answer |

Interactive OpenAPI documentation is available at `/docs` on API port 8000.

## Failure behavior

Upload errors are rejected synchronously. Extraction failures are stored on the document and surfaced in the UI. Retryable operating-system errors use exponential Celery backoff. Provider errors become sanitized `502` responses; credentials are never included.
