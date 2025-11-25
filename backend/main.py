from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.http import router as http_router
from .api.websocket import router as ws_router
from .config import FRONTEND_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    import torch
    from .config import WHISPER_MODEL
    from .whisper.model import get_model

    logger.info("CUDA available: %s", torch.cuda.is_available())
    logger.info("CUDA version: %s", torch.version.cuda)
    logger.info("Loading Whisper model '%s'...", WHISPER_MODEL)

    get_model()
    logger.info("Whisper model '%s' is ready", WHISPER_MODEL)
    yield


app = FastAPI(
    title="whisper-stream",
    description="Локальный прототип: микрофон → WebSocket → Whisper → текст",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.include_router(http_router)
app.include_router(ws_router)
