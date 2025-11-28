# Whisper stream

Сервис потокового распознавания речи с использованием faster-whisper, WebSocket и FastAPI.

## Системные требования

### Для разработки

- ОС: Windows 10+ / Linux x86_64 / macOS (только CPU)
- Python: 3.10–3.12
- GPU Linux: NVIDIA GPU + NVIDIA Driver (опционально)
- GPU Windows: NVIDIA GPU + NVIDIA Driver + CUDA Toolkit 12 + cuDNN 9 (опционально)

### Для деплоя или обычного запуска в Docker:

- ОС: Windows 10+ / Linux x86_64 / macOS (только CPU)
- Docker + Docker Compose
- GPU Linux: NVIDIA GPU + NVIDIA Driver + NVIDIA Container Toolkit (опционально)
- GPU Windows: NVIDIA GPU + NVIDIA Driver (опционально)

## Установка и запуск

```bash
  git clone https://github.com/NikolaiT1986/whisper-stream.git
  cd whisper-stream
```

### Для Docker:

1-й запуск (или при изменениях в коде):

```bash
  docker compose up -d --build --wait
```

Повторные запуски без пересборки:

```bash
  docker compose up -d --wait
```

Остановить и удалить контейнеры:

```bash
  docker compose down
```

### Без Docker

#### Виртуальное окружение для Linux / macOS / Windows (Git Bash)

```bash
  python -m venv .venv
  source .venv/Scripts/activate
```

#### Установка зависимостей

```bash
  python -m pip install --upgrade pip # опционально
```

```bash
  pip install -r backend/requirements.txt
```

#### Запуск приложения

Windows (Git Bash)

```bash
  # example path-to-your-cudnn-bin/version: C:/Program Files/NVIDIA/CUDNN/v9.16/bin/12.9
  export CUDA_BIN_PATH='<path-to-your-cudnn-bin/version>'
  uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Linux / macOS

```bash
  uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

После запуска приложение будет доступно по адресу: http://localhost:8000/

## Настройки конфигурации

- Параметры конфигурации можно задавать через переменные окружение в терминале или в
  [`docker-compose.yml`](docker-compose.yml).
- Перечень всех параметров с описанием находится в фале [`backend/config.py`](backend/config.py).

Лицензия [MIT](https://opensource.org/licenses/MIT)