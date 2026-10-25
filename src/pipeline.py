from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from uuid import uuid4
from collections.abc import Callable
from src.adapters.interfaces import LLM, PdfParser, Store, TTS
from src.adapters.llm_ollama import OllamaLLM
from src.adapters.pdf_pymupdf import PyMuPdfParser
from src.adapters.store_sqlite import SqliteStore
from src.adapters.tts_piper import PiperTTS
from src.config import settings
from src.domain.chunker import chunk_text
from src.domain.prompts import chunk_prompt, summary_prompt
from src.domain.schemas import ChunkOutput, Kit, Summary
from src.observability import span


def build_kit(
    file_bytes: bytes,
    filename: str,
    tts_provider: str | None = None,
    *,
    llm: LLM | None = None,
    parser: PdfParser | None = None,
    tts: TTS | None = None,
    store: Store | None = None,
    progress: Callable[[str, int, str], None] | None = None,
) -> Kit:
    report = progress or (lambda _step, _pct, _note: None)
    with span("extract"):
        text = (parser or PyMuPdfParser()).extract(file_bytes)
    chunks = chunk_text(text, settings.max_chunk_tokens)
    report("chunking", 15, f"Splitting into {len(chunks)} sections.")
    model = llm or OllamaLLM()
    outputs: list[ChunkOutput] = []
    with ThreadPoolExecutor(max_workers=settings.max_workers) as executor:
        futures = {executor.submit(model.generate_json, chunk_prompt(chunk, i), ChunkOutput): i for i, chunk in enumerate(chunks)}
        for future in as_completed(futures):
            try:
                outputs.append(future.result())
            except Exception:
                continue
            report("cards", 45, f"{sum(len(item.flashcards) for item in outputs)} cards written so far.")
    outputs.sort(key=lambda item: item.flashcards[0].source_chunk if item.flashcards else 0)
    key_points = [point for output in outputs for point in output.key_points]
    summary = model.generate_json(summary_prompt(key_points), Summary)
    kit = Kit(
        id=uuid4().hex,
        title=Path(filename).stem.replace("-", " ").replace("_", " ").title(),
        summary=summary,
        flashcards=[card for output in outputs for card in output.flashcards],
        quiz=[question for output in outputs for question in output.quiz],
    )
    if tts_provider or settings.tts_provider:
        voice = tts or PiperTTS()
        audio_path = settings.data_dir / "audio" / f"{kit.id}.wav"
        try:
            kit.audio_path = str(voice.speak(summary.brief_script, audio_path))
        except (OSError, RuntimeError):
            kit.audio_path = None
    (store or SqliteStore()).save_kit(kit)
    report("done", 100, "Study kit ready.")
    return kit
