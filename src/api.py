import json
import queue
import threading
from collections.abc import Iterator
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.store_sqlite import SqliteStore
from src.config import settings
from src.pipeline import build_kit

app = FastAPI(title="Sloth Study API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_store() -> SqliteStore:
    return SqliteStore()


def _event(step: str, pct: int, note: str, **extra: str) -> str:
    payload = {"step": step, "pct": pct, "note": note, **extra}
    return f"data: {json.dumps(payload)}\n\n"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/kits")
async def create_kit(
    file: UploadFile = File(...),
    tts_provider: str = Form("piper"),
) -> StreamingResponse:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    filename = file.filename or "study-notes.pdf"
    return _kit_stream(data, filename, tts_provider)


def _kit_stream(data: bytes, filename: str, tts_provider: str) -> StreamingResponse:
    def stream() -> Iterator[str]:
        yield _event("upload", 5, f"Reading {filename}.")
        updates: queue.Queue[tuple[str, int, str] | None] = queue.Queue()
        result = []
        error = []

        def run_build():
            try:
                result.append(build_kit(
                    data,
                    filename,
                    tts_provider,
                    progress=lambda step, pct, note: updates.put((step, pct, note)),
                ))
            except Exception as build_error:
                error.append(build_error)
            finally:
                updates.put(None)

        threading.Thread(target=run_build, daemon=True).start()
        while True:
            update = updates.get()
            if update is None:
                break
            step, pct, note = update
            yield _event(step, pct, note)
        if error:
            yield _event("error", 100, "The study kit could not be built.")
            raise error[0]
        kit = result[0]
        yield _event("done", 100, "Study kit ready.", kit_id=kit.id)

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/samples")
def list_samples() -> list[str]:
    samples_dir = Path("samples")
    return sorted(path.name for path in samples_dir.glob("*.pdf"))


@app.post("/api/samples/{filename}")
def create_sample_kit(filename: str, tts_provider: str = "piper") -> StreamingResponse:
    sample_path = (Path("samples") / filename).resolve()
    samples_dir = Path("samples").resolve()
    if samples_dir not in sample_path.parents or sample_path.suffix.lower() != ".pdf" or not sample_path.is_file():
        raise HTTPException(status_code=404, detail="Sample not found")
    return _kit_stream(sample_path.read_bytes(), sample_path.name, tts_provider)


@app.get("/api/kits")
def list_kits() -> list[dict[str, str]]:
    return [{"id": kit_id, "title": title} for kit_id, title in get_store().list_kits()]


@app.get("/api/kits/{kit_id}")
def get_kit(kit_id: str):
    try:
        return get_store().get_kit(kit_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Kit not found") from error


@app.get("/api/audio/{kit_id}")
def get_audio(kit_id: str):
    try:
        kit = get_store().get_kit(kit_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Kit not found") from error
    if not kit.audio_path:
        raise HTTPException(status_code=404, detail="Audio is not available")
    audio_path = Path(kit.audio_path).resolve()
    data_root = settings.data_dir.resolve()
    if data_root not in audio_path.parents or not audio_path.is_file():
        raise HTTPException(status_code=404, detail="Audio is not available")
    return FileResponse(audio_path, media_type="audio/wav", filename=audio_path.name)
