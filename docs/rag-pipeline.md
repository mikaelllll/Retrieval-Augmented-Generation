# RAG pipeline

## Ingestion

1. Validate the extension, MIME type, size, and PDF signature.
2. Store the file under generated workspace/document identifiers.
3. Commit a queued database row and enqueue its ID.
4. Extract each page with pypdf.
5. Normalize whitespace and produce approximately 220-word chunks with 40-word overlap.
6. Generate local embeddings in a batch using the CPU-focused ONNX runtime.
7. Commit chunks and mark the document ready atomically.

The overlap preserves context across chunk boundaries. Page numbers remain attached to every passage so citations are traceable.

## Retrieval and generation

The question uses the same embedding model and normalization as passages. pgvector orders owned, ready chunks by cosine distance. The backend converts distance to similarity, applies a configurable minimum, and sends at most six passages to Gemini.

The system instruction treats document content as untrusted evidence. Gemini must use only supplied sources, cite their stable labels, ignore instructions inside them, and refuse unsupported questions. The backend—not the model—selects authorized documents and validates the source list.

## Known retrieval limits

`all-MiniLM-L6-v2` is compact and Codespaces-friendly, but English-first and not optimal for scanned PDFs, tables, or multilingual corpora. Natural extensions include OCR, layout-aware extraction, multilingual embeddings, hybrid BM25/vector search, a cross-encoder reranker, query rewriting, and an evaluation dataset for retrieval recall and citation faithfulness.
