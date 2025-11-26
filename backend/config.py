from pathlib import Path

# ===== Пути =====
BASE_DIR = Path(__file__).resolve().parent.parent  # корень проекта (backend/)
FRONTEND_DIR = BASE_DIR / "frontend"  # папка с фронтендом
MODELS_DIR = BASE_DIR / "models"  # папка для весов faster-whisper

# ===== Аудио и VAD =====
SAMPLE_RATE = 16000  # частота дискретизации, Гц (float32)
BYTES_PER_SAMPLE = 4  # размер одного семпла, байт

VOICE_START_THRESHOLD = 0.010  # RMS-порог, выше — считаем, что речь началась
VOICE_CONTINUE_THRESHOLD = 0.006  # RMS-порог, ниже — считаем тишину (гистерезис)

PRE_SPEECH_SECONDS = 0.3  # сколько тишины до начала речи буферизуем
MIN_SPEECH_SECONDS = 1.0  # минимальная длительность фразы, чтобы отправлять
MAX_SILENCE_SECONDS = 0.5  # длительность паузы тишины, считаем конец фразы
MAX_SEGMENT_SECONDS = 0.0  # ограничение длины фразы; 0.0 = без ограничения

PRE_SPEECH_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * PRE_SPEECH_SECONDS)
MAX_SEGMENT_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * MAX_SEGMENT_SECONDS)

# ===== Whisper =====

# Доступные модели (model_size):
#   tiny, tiny.en
#   base, base.en
#   small, small.en
#   medium, medium.en
#   large-v1, large-v2, large-v3
#   large-v3-turbo, turbo
#   distil-large-v3
#
WHISPER_MODEL: str = "large-v3-turbo"  # текущая модель faster-whisper
WHISPER_DEVICE: str = "cuda"  # "cpu", "cuda" или "cuda:0", "cuda:1" для конкретного устройства
WHISPER_LANGUAGE: str | None = None  # None = автоопределение языка, "ru", "en", ...
WHISPER_USE_CONTEXT: bool = True  # True | False использовать ли контекст предыдущих сегментов
