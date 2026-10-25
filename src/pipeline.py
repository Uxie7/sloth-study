from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from uuid import uuid4
from collections.abc import Callable
from src.adapters.interfaces import LLM, PdfParser, Store, TTS
from src.adapters.llm_ollama import OllamaLLM
from src.adapters.pdf_pymupdf import PyMuPdfParser
from src.adapters.store_sqlite import SqliteStore
from src.adapters.tts_piper import PiperTTS
from src.adapters.tts_elevenlabs import ElevenLabsTTS
from src.config import settings
from src.domain.chunker import chunk_text
from src.domain.prompts import chunk_prompt, summary_prompt
from src.domain.schemas import ChunkOutput, Kit, Summary
from src.domain.schemas import QuizQuestion
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
            except Exception as error:
                chunk_index = futures[future]
                report("chunk_failed", 45, f"Section {chunk_index + 1} was skipped: {error}")
                continue
            report("cards", 45, f"{sum(len(item.flashcards) for item in outputs)} cards written so far.")
    outputs.sort(key=lambda item: item.flashcards[0].source_chunk if item.flashcards else 0)
    for output in outputs:
        if not output.key_points:
            output.key_points = [card.answer for card in output.flashcards[:5]]
        if len(output.quiz) < 5:
            generated_quiz = [
                QuizQuestion(
                    question=card.question,
                    options=[card.answer, "Not stated in the source", "An unrelated example", "None of these"],
                    correct_index=0,
                    explanation="The flashcard answer is the grounded answer from the source material.",
                    source_chunk=card.source_chunk,
                )
                for card in output.flashcards[:5]
            ]
            output.quiz = (output.quiz + generated_quiz)[:5]
    key_points = [point for output in outputs for point in output.key_points]
    summary = model.generate_json(summary_prompt(key_points), Summary)
    kit = Kit(
        id=uuid4().hex,
        title=Path(filename).stem.replace("-", " ").replace("_", " ").title(),
        summary=summary,
        flashcards=[card for output in outputs for card in output.flashcards],
        quiz=[question for output in outputs for question in output.quiz],
        chunks=chunks,
    )
    selected_tts = tts_provider or settings.tts_provider
    if selected_tts not in {"", "none", "off", "disabled"}:
        voice = tts or (ElevenLabsTTS() if selected_tts == "elevenlabs" else PiperTTS())
        audio_path = settings.data_dir / "audio" / f"{kit.id}.wav"
        try:
            kit.audio_path = str(voice.speak(summary.brief_script, audio_path))
        except (OSError, RuntimeError) as error:
            report("audio_failed", 90, f"Audio could not be generated: {error}")
            kit.audio_path = None
    (store or SqliteStore()).save_kit(kit)
    report("done", 100, "Study kit ready.")
    return kit
