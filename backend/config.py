from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# ====== Аудио-параметры и VAD ======
SAMPLE_RATE = 16000          # 16 kHz float32
BYTES_PER_SAMPLE = 4         # float32

# пороги VAD (при необходимости можно подстроить)
VOICE_START_THRESHOLD = 0.010      # RMS выше -> считаем, что речь началась
VOICE_CONTINUE_THRESHOLD = 0.006   # ниже -> считаем тишину (гистерезис)

PRE_SPEECH_SECONDS = 0.3     # сколько "тишины до речи" сохранять
MIN_SPEECH_SECONDS = 1.0     # минимальная длина фразы, чтобы её отправлять
MAX_SILENCE_SECONDS = 0.5    # пауза после речи, означающая конец фразы
MAX_SEGMENT_SECONDS = 0.0    # 25.0 = защита от бесконечной фразы, 0.0 = без ограничения

PRE_SPEECH_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * PRE_SPEECH_SECONDS)
MAX_SEGMENT_BYTES = int(SAMPLE_RATE * BYTES_PER_SAMPLE * MAX_SEGMENT_SECONDS)

WHISPER_MODEL = "large-v3"  # tiny | base | small | medium | large-v3
WHISPER_LANGUAGE = None # None | "ru" | "en"
WHISPER_USE_GPU = True # False = CPU | True = GPU