from pathlib import Path
from src.adapters.tts_piper import PiperTTS


class ElevenLabsTTS:
    def __init__(self, fallback: PiperTTS | None = None):
        self.fallback = fallback or PiperTTS()

    def speak(self, text: str, out_path: Path) -> Path:
        # The optional provider is deliberately deferred until Phase 2 configuration.
        return self.fallback.speak(text, out_path)
