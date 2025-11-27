from __future__ import annotations

import os

if cuda_bin_path := os.environ.get("CUDA_BIN_PATH"):
    os.environ["PATH"] = cuda_bin_path + os.pathsep + os.environ["PATH"]

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import logging
import numpy as np
import ctranslate2
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.http import router as http_router
from .api.websocket import router as ws_router
from .config import FRONTEND_DIR, WHISPER_DEVICE, WHISPER_LANGUAGE

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    from .config import WHISPER_MODEL
    from .whisper.model import get_model

    cuda_supported = bool(ctranslate2.get_supported_compute_types("cuda"))

    logger.info("Whisper device is: %s", WHISPER_DEVICE)
    logger.info("Available GPU support: %s", cuda_supported)
    logger.info("Whisper language: %s", WHISPER_LANGUAGE or "auto")

    if WHISPER_DEVICE.lower() == "cuda" and not cuda_supported:
        raise RuntimeError("WHISPER_DEVICE=cuda, но CUDA compute types недоступны!")

    logger.info("Loading Whisper model '%s'...", WHISPER_MODEL)
    try:
        model = get_model()
        audio = np.zeros(0, dtype=np.float32)
        _segments, _info = model.transcribe(audio)
    except Exception as e:
        raise RuntimeError(e)
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
