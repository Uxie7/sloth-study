from pathlib import Path
from typing import Protocol, TypeVar
from pydantic import BaseModel
from src.domain.schemas import Kit

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    def generate_json(self, prompt: str, schema: type[T]) -> T: ...


class TTS(Protocol):
    def speak(self, text: str, out_path: Path) -> Path: ...


class PdfParser(Protocol):
    def extract(self, data: bytes) -> str: ...


class Store(Protocol):
    def save_kit(self, kit: Kit) -> None: ...
    def get_kit(self, kit_id: str) -> Kit: ...
    def list_kits(self) -> list[tuple[str, str]]: ...
