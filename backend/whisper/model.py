from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

from ..config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    MODELS_DIR,
    WHISPER_LANGUAGE,
    WHISPER_USE_CONTEXT,
)

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_model() -> WhisperModel:
    return WhisperModel(
        str(Path(MODELS_DIR) / WHISPER_MODEL),
        device=WHISPER_DEVICE,
        compute_type="int8_float16" if WHISPER_DEVICE == "cuda" else "int8",
    )


@lru_cache(maxsize=1)
def get_language() -> str | None:
    return (
        "en" if WHISPER_LANGUAGE and WHISPER_LANGUAGE.lower().endswith(".en")
        else WHISPER_LANGUAGE
    )


async def transcribe_chunk(raw_bytes: bytes) -> str:
    if not raw_bytes:
        return ""

    audio = np.frombuffer(raw_bytes, dtype=np.float32)
    if audio.size == 0:
        return ""

    try:
        segments, info = get_model().transcribe(
            audio,
            language=get_language(),
            beam_size=1,
            condition_on_previous_text=WHISPER_USE_CONTEXT,
        )
    except Exception as e:
        logger.exception("Whisper error during transcription: %s", e)
        return ""

    return " ".join(seg.text for seg in segments).strip()
