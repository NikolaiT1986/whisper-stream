from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import numpy as np
import whisper

from ..config import (
    WHISPER_MODEL,
    WHISPER_LANGUAGE,
    WHISPER_USE_GPU,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_model():
    """Лениво загрузить и закэшировать модель Whisper."""
    return whisper.load_model(WHISPER_MODEL)


async def transcribe_chunk(raw_bytes: bytes) -> str:
    """Преобразовать PCM float32 16 kHz в текст с помощью Whisper."""
    if not raw_bytes:
        return ""

    audio = np.frombuffer(raw_bytes, dtype=np.float32).copy()
    if audio.size == 0:
        return ""

    try:
        result: dict[str, Any] = get_model().transcribe(
            audio=audio,
            language=WHISPER_LANGUAGE,
            fp16=WHISPER_USE_GPU,
            condition_on_previous_text=False,
        )
    except Exception as e:
        logger.exception("Whisper error during transcription: %s", e)
        return ""

    text = (result.get("text") or "").strip()
    return text
