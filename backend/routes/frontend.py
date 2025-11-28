from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse

from ..config import FRONTEND_DIR

router = APIRouter()


@router.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
