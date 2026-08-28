import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models import Document
from app.schemas import DocumentOut
from app.security import workspace_id
from app.tasks import process_document

router = APIRouter(prefix="/documents", tags=["documents"])
WorkspaceDep = Annotated[uuid.UUID, Depends(workspace_id)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
PdfUpload = Annotated[UploadFile, File()]


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    workspace: WorkspaceDep,
    session: SessionDep,
) -> list[Document]:
    result = await session.scalars(
        select(Document)
        .where(Document.workspace_id == workspace)
        .order_by(Document.created_at.desc())
    )
    return list(result)


@router.post("", response_model=DocumentOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: PdfUpload,
    workspace: WorkspaceDep,
    session: SessionDep,
) -> Document:
    filename = file.filename or ""
    if file.content_type != "application/pdf" or not filename.lower().endswith(".pdf"):
        raise HTTPException(415, "Only PDF documents are supported")
    content = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"PDF exceeds the {settings.max_upload_mb} MB limit")
    if not content.startswith(b"%PDF"):
        raise HTTPException(400, "The uploaded file is not a valid PDF")
    document_id = uuid.uuid4()
    directory = Path(settings.upload_dir) / str(workspace)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{document_id}.pdf"
    path.write_bytes(content)
    document = Document(
        id=document_id,
        workspace_id=workspace,
        filename=Path(filename).name[:255],
        storage_path=str(path),
        content_type=file.content_type,
        size_bytes=len(content),
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    process_document.delay(str(document.id))
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    workspace: WorkspaceDep,
    session: SessionDep,
) -> None:
    document = await session.scalar(
        select(Document).where(Document.id == document_id, Document.workspace_id == workspace)
    )
    if not document:
        raise HTTPException(404, "Document not found")
    path = document.storage_path
    await session.delete(document)
    await session.commit()
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
