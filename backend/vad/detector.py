from __future__ import annotations

from typing import Optional

import numpy as np

from ..config import (
    SAMPLE_RATE,
    BYTES_PER_SAMPLE,
    PRE_SPEECH_BYTES,
    MAX_SEGMENT_BYTES,
    VOICE_START_THRESHOLD,
    VOICE_CONTINUE_THRESHOLD,
    MIN_SPEECH_SECONDS,
    MAX_SILENCE_SECONDS,
)
from ..whisper.model import transcribe_chunk


class VADState:
    """Состояние VAD для потокового распознавания речи (PCM float32, 16 kHz)."""

    def __init__(self) -> None:
        self.state: str = "idle"  # "idle" или "speech"

        self.pre_speech_buffer = bytearray()  # последние PRE_SPEECH_SECONDS до начала речи
        self.segment_buffer = bytearray()  # накопленные байты текущей фразы

        self.speech_duration: float = 0.0
        self.silence_duration: float = 0.0

    async def process_chunk(self, raw: bytes) -> Optional[str]:
        """
        Обработать 1 audio chunk.

        :param raw: PCM float32, 16 kHz.
        :return: текст завершённой фразы или None, если фраза ещё продолжается.
        """
        if not raw:
            return None

        samples_count = len(raw) // BYTES_PER_SAMPLE
        duration_sec = samples_count / float(SAMPLE_RATE)

        audio = np.frombuffer(raw, dtype=np.float32)
        if audio.size == 0:
            return None

        energy = float(np.sqrt(np.mean(audio * audio)))

        # ===== idle: ждём начала речи =====
        if self.state == "idle":
            self.pre_speech_buffer.extend(raw)
            if len(self.pre_speech_buffer) > PRE_SPEECH_BYTES:
                overflow = len(self.pre_speech_buffer) - PRE_SPEECH_BYTES
                del self.pre_speech_buffer[:overflow]

            if energy >= VOICE_START_THRESHOLD:
                self.state = "speech"
                # добавляем в сегмент кусок "разгона" перед фразой
                self.segment_buffer.extend(self.pre_speech_buffer)
                self.pre_speech_buffer.clear()
                self.segment_buffer.extend(raw)
                self.speech_duration = duration_sec
                self.silence_duration = 0.0

            return None

        # ===== speech: внутри фразы =====
        self.segment_buffer.extend(raw)
        self.speech_duration += duration_sec

        if 0 < MAX_SEGMENT_BYTES < len(self.segment_buffer):
            print("force cut: segment too long")
            text = await transcribe_chunk(bytes(self.segment_buffer))
            self._reset()
            return text or None

        if energy < VOICE_CONTINUE_THRESHOLD:
            self.silence_duration += duration_sec
        else:
            self.silence_duration = 0.0

        if self.silence_duration >= MAX_SILENCE_SECONDS:
            text: Optional[str] = None

            if self.speech_duration >= MIN_SPEECH_SECONDS:
                pcm_bytes = bytes(self.segment_buffer)
                print(
                    f"final segment: duration={self.speech_duration:.2f}s, "
                    f"bytes={len(pcm_bytes)}, energy={energy:.4f}"
                )
                text = await transcribe_chunk(pcm_bytes)
                print("recognized segment:", repr(text))

            self._reset()
            return text or None

        return None

    async def flush(self) -> Optional[str]:
        """Дораспознать остаток фразы, если клиент отключился посреди речи."""
        if (
                self.state == "speech"
                and self.segment_buffer
                and self.speech_duration >= MIN_SPEECH_SECONDS
        ):
            pcm_bytes = bytes(self.segment_buffer)
            text = await transcribe_chunk(pcm_bytes)
            self._reset()
            return text or None

        return None

    def _reset(self) -> None:
        """
        Сбросить состояние в начальное.

        Буфер pre_speech_buffer не очищается: он заполняется заново
        при следующем состоянии idle.
        """
        self.state = "idle"
        self.segment_buffer.clear()
        self.speech_duration = 0.0
        self.silence_duration = 0.0
