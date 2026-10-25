from src.domain.chunker import chunk_text
from src.domain.schemas import Kit, Summary
from src.domain.scoring import score_quiz


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
