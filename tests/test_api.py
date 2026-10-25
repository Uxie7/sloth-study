from fastapi.testclient import TestClient

from src import api
from src.domain.schemas import Flashcard, Kit, QuizQuestion, Summary


def _kit() -> Kit:
    return Kit(
        id="api-fixture",
        title="API Fixture",
        summary=Summary(bullets=["A key point"], brief_script="A short script."),
        flashcards=[Flashcard(question="What is tested?", answer="The API", source_chunk=0)],
        quiz=[QuizQuestion(
            question="Which option is correct?",
            options=["No", "Yes", "Maybe", "Later"],
            correct_index=1,
            explanation="Yes is correct.",
            source_chunk=0,
        )],
    )


def test_create_kit_streams_completion_and_persists(monkeypatch):
    stored = {}
    fixture = _kit()

    class Store:
        def save_kit(self, kit):
            stored[kit.id] = kit

        def get_kit(self, kit_id):
            return stored[kit_id]

        def list_kits(self):
            return [(kit.id, kit.title) for kit in stored.values()]

    def fake_build(*args, progress=None, **kwargs):
        progress("chunking", 15, "Splitting into 1 section.")
        progress("done", 100, "Study kit ready.")
        stored[fixture.id] = fixture
        return fixture

    monkeypatch.setattr(api, "build_kit", fake_build)
    monkeypatch.setattr(api, "get_store", lambda: Store())

    response = TestClient(api.app).post(
        "/api/kits",
        files={"file": ("notes.pdf", b"pdf bytes", "application/pdf")},
        data={"tts_provider": "piper"},
    )

    assert response.status_code == 200
    assert '"step": "done"' in response.text
    assert f'"kit_id": "{fixture.id}"' in response.text
    assert stored[fixture.id].title == "API Fixture"


def test_list_and_get_kit_round_trip(monkeypatch):
    fixture = _kit()

    class Store:
        def list_kits(self):
            return [(fixture.id, fixture.title)]

        def get_kit(self, kit_id):
            if kit_id != fixture.id:
                raise KeyError(kit_id)
            return fixture

    monkeypatch.setattr(api, "get_store", lambda: Store())
    client = TestClient(api.app)

    assert client.get("/api/kits").json() == [{"id": fixture.id, "title": fixture.title}]
    assert client.get(f"/api/kits/{fixture.id}").json()["title"] == fixture.title
    assert client.get("/api/kits/missing").status_code == 404
