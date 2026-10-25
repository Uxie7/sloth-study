import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "gemma3:4b")
    tts_provider: str = os.getenv("TTS_PROVIDER", "piper")
    piper_model_path: str = os.getenv("PIPER_MODEL_PATH", "./models/en_US-lessac-medium.onnx")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data"))
    max_chunk_tokens: int = int(os.getenv("MAX_CHUNK_TOKENS", "1500"))
    max_workers: int = int(os.getenv("MAX_WORKERS", "3"))


settings = Settings()
