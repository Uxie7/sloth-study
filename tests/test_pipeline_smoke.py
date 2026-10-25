from src.domain.chunker import chunk_text
from src.domain.schemas import Kit, Summary
from src.domain.scoring import score_quiz
from src.pipeline import build_kit
from src.adapters.store_sqlite import SqliteStore
from dataclasses import replace
from src.config import settings
from src.adapters.tts_elevenlabs import ElevenLabsTTS


def test_phase1_chunker_splits_correctly():
    chunks = chunk_text(("word " * 100) + "\n\n" + ("next " * 100), max_tokens=150)
    assert len(chunks) == 2
    assert all(len(chunk.split()) <= 150 for chunk in chunks)


def test_phase1_schemas_valid():
    kit = Kit(
        id="fixture",
        title="Fixture",
        summary=Summary(bullets=["One point"], brief_script="A brief."),
        flashcards=[{"question": "What is this?", "answer": "A fixture", "source_chunk": 0}],
        quiz=[{"question": "Which?", "options": ["A", "B", "C", "D"], "correct_index": 1, "explanation": "B.", "source_chunk": 0}],
    )
    assert kit.title == "Fixture"
    assert score_quiz(kit.quiz, [1]) == 1


class FakeParser:
    def extract(self, data):
        return "First paragraph with study material.\n\nSecond paragraph with more study material."


class FakeLLM:
    def __init__(self):
        self.chunk_calls = 0

    def generate_json(self, prompt, schema):
        if schema.__name__ == "ChunkOutput":
            self.chunk_calls += 1
            if self.chunk_calls == 1:
                raise ValueError("malformed response")
            return schema(
                flashcards=[{"question": "What is tested?", "answer": "A fact", "source_chunk": 0}],
                quiz=[{"question": "Which?", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "A.", "source_chunk": 0}],
                key_points=["A fact"],
            )
        return schema(bullets=["A fact"], brief_script="A short brief.")


class FakeTTS:
    def speak(self, text, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"audio")
        return out_path


def test_phase3_bad_chunk_is_skipped_and_audio_is_created(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.pipeline.settings",
        replace(settings, data_dir=tmp_path, max_chunk_tokens=5, max_workers=1),
    )
    events = []
    kit = build_kit(
        b"notes",
        "notes.pdf",
        "piper",
        llm=FakeLLM(),
        parser=FakeParser(),
        tts=FakeTTS(),
        store=SqliteStore(":memory:"),
        progress=lambda step, pct, note: events.append((step, pct, note)),
    )
    assert len(kit.flashcards) >= 1
    assert any(event[0] == "chunk_failed" for event in events)
    assert kit.audio_path is not None


def test_phase3_sqlite_roundtrip():
    source = Kit(
        id="roundtrip",
        title="Roundtrip",
        summary=Summary(bullets=["Point"], brief_script="Brief"),
        flashcards=[],
        quiz=[],
    )
    store = SqliteStore(":memory:")
    store.save_kit(source)
    assert store.get_kit("roundtrip").title == "Roundtrip"


def test_phase3_elevenlabs_without_key_uses_piper_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)

    class Fallback:
        def speak(self, text, out_path):
            out_path.write_bytes(b"fallback")
            return out_path

    target = tmp_path / "voice.wav"
    assert ElevenLabsTTS(Fallback()).speak("brief", target) == target
    assert target.read_bytes() == b"fallback"
