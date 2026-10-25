from pathlib import Path
import os
from src.adapters.tts_piper import PiperTTS


class ElevenLabsTTS:
    def __init__(self, fallback: PiperTTS | None = None):
        self.fallback = fallback or PiperTTS()

    def speak(self, text: str, out_path: Path) -> Path:
        api_key = os.getenv("ELEVENLABS_API_KEY", "")
        if not api_key:
            return self.fallback.speak(text, out_path)
        try:
            from elevenlabs.client import ElevenLabs
            audio = ElevenLabs(api_key=api_key).text_to_speech.convert(
                text=text,
                voice_id="Rachel",
                model_id="eleven_multilingual_v2",
            )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("wb") as output:
                for chunk in audio:
                    output.write(chunk)
            return out_path
        except (OSError, RuntimeError, ImportError):
            return self.fallback.speak(text, out_path)
