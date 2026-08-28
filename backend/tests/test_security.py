import pytest
from fastapi import HTTPException

from app.security import gemini_key, workspace_id


@pytest.mark.asyncio
async def test_workspace_id_rejects_invalid_uuid() -> None:
    with pytest.raises(HTTPException) as error:
        await workspace_id("not-a-uuid")
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_gemini_key_is_trimmed() -> None:
    key = "x" * 30
    assert await gemini_key(f"  {key}  ") == key


@pytest.mark.asyncio
async def test_gemini_key_rejects_short_value() -> None:
    with pytest.raises(HTTPException):
        await gemini_key("short")

