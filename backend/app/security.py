import uuid

from fastapi import Header, HTTPException, status


async def workspace_id(x_workspace_id: str = Header(..., alias="X-Workspace-ID")) -> uuid.UUID:
    try:
        return uuid.UUID(x_workspace_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace ID"
        ) from exc


async def gemini_key(x_gemini_api_key: str = Header(..., alias="X-Gemini-API-Key")) -> str:
    key = x_gemini_api_key.strip()
    if len(key) < 20 or len(key) > 300:
        raise HTTPException(status_code=400, detail="Invalid Gemini API key format")
    return key
