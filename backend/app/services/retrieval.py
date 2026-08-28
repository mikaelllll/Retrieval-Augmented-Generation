import uuid
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Chunk, Document, DocumentStatus
from app.schemas import SourceOut
from app.services.embeddings import embed_query

OVERVIEW_PHRASES = (
    "what is this document about",
    "what is the document about",
    "what are these documents about",
    "summarize this document",
    "summarise this document",
    "summarize the document",
    "give me a summary",
    "give me an overview",
    "document overview",
)


def is_overview_question(question: str) -> bool:
    normalized = " ".join(question.casefold().strip().split()).rstrip("?.!")
    return any(phrase in normalized for phrase in OVERVIEW_PHRASES)


async def retrieve_overview(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    document_ids: list[uuid.UUID],
) -> list[SourceOut]:
    statement = (
        select(Chunk, Document)
        .join(Document, Document.id == Chunk.document_id)
        .where(Document.workspace_id == workspace_id, Document.status == DocumentStatus.ready)
        .order_by(Document.created_at.desc(), Chunk.position)
        .limit(settings.retrieval_limit)
    )
    if document_ids:
        statement = statement.where(Document.id.in_(document_ids))
    rows = (await session.execute(statement)).all()
    return [
        SourceOut(
            document_id=document.id,
            filename=document.filename,
            page_number=chunk.page_number,
            content=chunk.content,
            similarity=None,
            retrieval_method="overview",
            citation=f"[S{index}]",
        )
        for index, (chunk, document) in enumerate(rows, start=1)
    ]


async def retrieve(
    session: AsyncSession,
    workspace_id: uuid.UUID,
    question: str,
    document_ids: list[uuid.UUID],
) -> tuple[list[SourceOut], int]:
    started = perf_counter()
    if is_overview_question(question):
        sources = await retrieve_overview(session, workspace_id, document_ids)
        return sources, round((perf_counter() - started) * 1000)

    query_vector = embed_query(question)
    distance = Chunk.embedding.cosine_distance(query_vector)
    statement = (
        select(Chunk, Document, distance.label("distance"))
        .join(Document, Document.id == Chunk.document_id)
        .where(Document.workspace_id == workspace_id, Document.status == DocumentStatus.ready)
        .order_by(distance)
        .limit(settings.retrieval_limit)
    )
    if document_ids:
        statement = statement.where(Document.id.in_(document_ids))
    rows = (await session.execute(statement)).all()
    sources = []
    for index, (chunk, document, value) in enumerate(rows, start=1):
        similarity = max(0.0, 1.0 - float(value))
        if similarity < settings.similarity_threshold:
            continue
        sources.append(
            SourceOut(
                document_id=document.id,
                filename=document.filename,
                page_number=chunk.page_number,
                content=chunk.content,
                similarity=round(similarity, 4),
                retrieval_method="semantic",
                citation=f"[S{index}]",
            )
        )
    return sources, round((perf_counter() - started) * 1000)
