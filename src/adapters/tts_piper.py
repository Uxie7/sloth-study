import subprocess
from pathlib import Path
from src.config import settings


class PiperTTS:
    def speak(self, text: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        command = ["piper", "--model", settings.piper_model_path, "--output_file", str(out_path)]
        subprocess.run(command, input=text, text=True, check=True, capture_output=True)
        return out_path
