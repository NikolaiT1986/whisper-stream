from pathlib import Path

from faster_whisper.utils import download_model

from backend.config import WHISPER_MODEL, MODELS_DIR


def main():
    download_model(
        WHISPER_MODEL,
        output_dir=str(Path(MODELS_DIR) / WHISPER_MODEL),
        local_files_only=False,
        cache_dir=None,
    )


if __name__ == "__main__":
    main()
