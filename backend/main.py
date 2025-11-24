from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import whisper
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@lru_cache(maxsize=1)
def get_model():
    return whisper.load_model("base")


app = FastAPI(
    title="whisper-stream",
    description="Локальный прототип: микрофон → WebSocket → Whisper → текст",
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ====== Аудио-параметры и VAD ======
SAMPLE_RATE = 16000  # мы шлём 16 kHz float32
BYTES_PER_SAMPLE = 4  # float32

# пороги VAD (можно будет подкрутить под свой микрофон)
VOICE_START_THRESHOLD = 0.010  # RMS выше -> считаем, что речь началась
VOICE_CONTINUE_THRESHOLD = 0.006  # гистерезис: ниже -> считаем тишину

PRE_SPEECH_SECONDS = 0.3  # сколько "тишины до речи" сохранять (чтобы не отрезать начало)
MIN_SPEECH_SECONDS = 0.0  # минимальная длина фразы, чтобы вообще её отправлять
MAX_SILENCE_SECONDS = 1.0  # пауза после речи, означающая конец фразы
MAX_SEGMENT_SECONDS = 0.0  # 25.0 рекомендуется защита от бесконечной фразы, 0.0 = без ограничения

PRE_SPEECH_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * PRE_SPEECH_SECONDS)
MAX_SEGMENT_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * MAX_SEGMENT_SECONDS)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


async def transcribe_chunk(raw_bytes: bytes) -> str:
    """Преобразует сырые байты PCM float32 → текст через Whisper."""
    if not raw_bytes:
        return ""

    audio = np.frombuffer(raw_bytes, dtype=np.float32).copy()
    if audio.size == 0:
        return ""

    try:
        result: dict[str, Any] = get_model().transcribe(
            audio=audio,
            language="ru",
            fp16=False,
        )
    except Exception as e:
        print("Whisper error:", type(e).__name__, e)
        return ""

    text = (result.get("text") or "").strip()
    return text


@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket) -> None:
    await websocket.accept()
    print("Client connected")

    # состояние VAD
    state = "idle"  # "idle" | "speech"
    pre_speech_buffer = bytearray()  # последние PRE_SPEECH_SECONDS перед стартом речи
    segment_buffer = bytearray()  # текущая фраза (речь)

    speech_duration = 0.0  # сколько секунд "речи" в текущем сегменте
    silence_duration = 0.0  # сколько секунд тишины подряд во время речи

    try:
        while True:
            raw = await websocket.receive_bytes()
            if not raw:
                continue

            # вычисляем длительность чанка
            samples_count = len(raw) // BYTES_PER_SAMPLE
            duration_sec = samples_count / float(SAMPLE_RATE)

            # считаем энергию (RMS) для VAD
            audio = np.frombuffer(raw, dtype=np.float32)
            if audio.size == 0:
                continue
            energy = float(np.sqrt(np.mean(audio * audio)))

            # ====== IDLE: пока тишина, просто накапливаем пре-буфер ======
            if state == "idle":
                # добавляем в пре-буфер и обрезаем до PRE_SPEECH_SECONDS
                pre_speech_buffer.extend(raw)
                if len(pre_speech_buffer) > PRE_SPEECH_BYTES:
                    overflow = len(pre_speech_buffer) - PRE_SPEECH_BYTES
                    del pre_speech_buffer[:overflow]

                # если энергия поднялась выше порога — старт речи
                if energy >= VOICE_START_THRESHOLD:
                    state = "speech"
                    segment_buffer.extend(pre_speech_buffer)  # добавляем "разгон" перед фразой
                    pre_speech_buffer.clear()
                    segment_buffer.extend(raw)
                    speech_duration = duration_sec
                    silence_duration = 0.0
                else:
                    # всё ещё тишина — просто ждём
                    continue

            # ====== SPEECH: человек говорит (или только что говорил) ======
            elif state == "speech":
                segment_buffer.extend(raw)
                speech_duration += duration_sec

                # не даём сегменту вырасти бесконечно
                if 0 < MAX_SEGMENT_BYTES < len(segment_buffer):
                    print("force cut: segment too long")
                    text = await transcribe_chunk(bytes(segment_buffer))
                    if text:
                        await websocket.send_json({"text": text})

                    # сброс в idle
                    state = "idle"
                    segment_buffer.clear()
                    speech_duration = 0.0
                    silence_duration = 0.0
                    continue

                # обновляем тишину / речь
                if energy < VOICE_CONTINUE_THRESHOLD:
                    silence_duration += duration_sec
                else:
                    silence_duration = 0.0

                # если накопилось достаточно тишины — считаем фразу законченной
                if silence_duration >= MAX_SILENCE_SECONDS:
                    if speech_duration >= MIN_SPEECH_SECONDS:
                        pcm_bytes = bytes(segment_buffer)
                        print(
                            f"final segment: duration={speech_duration:.2f}s, "
                            f"bytes={len(pcm_bytes)}, energy={energy:.4f}"
                        )
                        text = await transcribe_chunk(pcm_bytes)
                        print("recognized segment:", repr(text))
                        if text:
                            await websocket.send_json({"text": text})

                    # сбрасываем состояние
                    state = "idle"
                    segment_buffer.clear()
                    speech_duration = 0.0
                    silence_duration = 0.0

    except WebSocketDisconnect:
        print("Client disconnected")

        # если пользователь отключился посреди речи — дораспознать остаток
        if state == "speech" and segment_buffer and speech_duration >= MIN_SPEECH_SECONDS:
            pcm_bytes = bytes(segment_buffer)
            text = await transcribe_chunk(pcm_bytes)
            if text:
                try:
                    await websocket.send_json({"text": text})
                except Exception:
                    pass

    except Exception as e:
        print("WebSocket error:", type(e).__name__, e)
        try:
            await websocket.close()
        except Exception:
            pass
