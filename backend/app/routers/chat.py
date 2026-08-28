import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.schemas import AskRequest, AskResponse, ProviderCheck
from app.security import gemini_key, workspace_id
from app.services.gemini import check_key, generate_answer, provider_error
from app.services.retrieval import retrieve

router = APIRouter(tags=["chat"])
WorkspaceDep = Annotated[uuid.UUID, Depends(workspace_id)]
GeminiKeyDep = Annotated[str, Depends(gemini_key)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/provider/check", response_model=ProviderCheck)
async def validate_provider(key: GeminiKeyDep) -> ProviderCheck:
    try:
        await check_key(key)
        return ProviderCheck(
            valid=True,
            model=settings.gemini_model,
            message="Gemini connection verified",
        )
    except Exception as exc:
        raise HTTPException(400, provider_error(exc)) from exc


@router.post("/chat/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    workspace: WorkspaceDep,
    key: GeminiKeyDep,
    session: SessionDep,
) -> AskResponse:
    sources, retrieval_ms = await retrieve(
        session, workspace, payload.question, payload.document_ids
    )
    if not sources:
        return AskResponse(
            answer=(
                "I could not find enough relevant evidence in the ready documents "
                "to answer that question."
            ),
            status="not_found",
            sources=[],
            model=settings.gemini_model,
            retrieval_ms=retrieval_ms,
            generation_ms=0,
        )
    try:
        answer, generation_ms = await generate_answer(key, payload.question, sources)
    except Exception as exc:
        raise HTTPException(502, provider_error(exc)) from exc
    return AskResponse(
        answer=answer,
        status="answered",
        sources=sources,
        model=settings.gemini_model,
        retrieval_ms=retrieval_ms,
        generation_ms=generation_ms,
    )
