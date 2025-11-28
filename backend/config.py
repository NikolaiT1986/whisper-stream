import os
from pathlib import Path


def resolve_device(value: str) -> str:
    value = value.lower().strip()
    return "cuda" + value[3:] if value.startswith("gpu") else value


# ===== Пути =====
BASE_DIR = Path(__file__).resolve().parent.parent  # корень проекта
FRONTEND_DIR = BASE_DIR / "frontend"  # статические файлы фронтенда
MODELS_DIR = BASE_DIR / "models"  # локальные веса faster-whisper

# ===== Аудио и VAD =====
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", 16000))  # частота PCM, Гц
BYTES_PER_SAMPLE = int(os.getenv("BYTES_PER_SAMPLE", 4))  # размер семпла, байт (float32 = 4)

VOICE_START_THRESHOLD = float(os.getenv("VOICE_START_THRESHOLD", 0.010))  # порог RMS для старта речи
VOICE_CONTINUE_THRESHOLD = float(os.getenv("VOICE_CONTINUE_THRESHOLD", 0.006))  # порог RMS для продолжения речи

PRE_SPEECH_SECONDS = float(os.getenv("PRE_SPEECH_SECONDS", 0.3))  # буфер тишины до начала речи
MIN_SPEECH_SECONDS = float(os.getenv("MIN_SPEECH_SECONDS", 1.0))  # минимальная длина фразы
MAX_SILENCE_SECONDS = float(os.getenv("MAX_SILENCE_SECONDS", 0.5))  # пауза, считающаяся концом фразы
MAX_SEGMENT_SECONDS = float(os.getenv("MAX_SEGMENT_SECONDS", 0.0))  # максимум длины фразы; 0 = без лимита

PRE_SPEECH_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * PRE_SPEECH_SECONDS)  # байты pre-speech буфера
MAX_SEGMENT_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * MAX_SEGMENT_SECONDS)  # байты для лимита фразы

# ===== Whisper =====
# tiny(.en), base(.en), small(.en), medium(.en), large-v1/v2/v3, large-v3-turbo, turbo, distil-large-v3
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base").lower()  # имя модели
WHISPER_DEVICE = resolve_device(os.getenv("WHISPER_DEVICE", "cpu"))  # "cpu", "cuda" | "cuda:0" | "cuda:1" (gpu)
WHISPER_LANGUAGE: str | None = os.getenv("WHISPER_LANGUAGE") or None  # язык ("ru", "en", ...), None = авто
# размер beam search: 1 = greedy, >1 = beam search (по умолчанию 1)
WHISPER_BEAM_SIZE: int | None = int(os.getenv("WHISPER_BEAM_SIZE", "1"))
# True | False использовать ли контекст предыдущих сегментов
WHISPER_USE_CONTEXT: bool = os.getenv("WHISPER_USE_CONTEXT", "true").lower() in ("1", "true", "yes", "on")
