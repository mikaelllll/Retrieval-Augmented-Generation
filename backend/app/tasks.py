import asyncio
import uuid

from pypdf import PdfReader
from sqlalchemy import delete, select

from app.database import SessionFactory
from app.models import Chunk, Document, DocumentStatus
from app.services.chunking import chunk_pages
from app.services.embeddings import embed_passages
from app.worker import celery


@celery.task(bind=True, autoretry_for=(OSError,), retry_backoff=True, max_retries=3)
def process_document(self, document_id: str) -> None:  # noqa: ARG001
    asyncio.run(_process_document(uuid.UUID(document_id)))


async def _process_document(document_id: uuid.UUID) -> None:
    async with SessionFactory() as session:
        document = await session.scalar(select(Document).where(Document.id == document_id))
        if not document:
            return
        document.status = DocumentStatus.processing
        await session.commit()
        try:
            reader = PdfReader(document.storage_path)
            pages = [page.extract_text() or "" for page in reader.pages]
            chunks = chunk_pages(pages)
            if not chunks:
                raise ValueError("No readable text was found in this PDF")
            embeddings = embed_passages([chunk.content for chunk in chunks])
            await session.execute(delete(Chunk).where(Chunk.document_id == document.id))
            session.add_all(
                [
                    Chunk(
                        document_id=document.id,
                        page_number=chunk.page_number,
                        position=chunk.position,
                        content=chunk.content,
                        token_estimate=max(1, len(chunk.content) // 4),
                        embedding=embedding,
                    )
                    for chunk, embedding in zip(chunks, embeddings, strict=True)
                ]
            )
            document.page_count = len(pages)
            document.chunk_count = len(chunks)
            document.status = DocumentStatus.ready
            document.error_message = None
        except Exception as exc:  # task boundary records a safe failure state
            document.status = DocumentStatus.failed
            document.error_message = str(exc)[:500]
        await session.commit()

