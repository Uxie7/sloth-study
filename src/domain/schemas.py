from pydantic import BaseModel, Field
from pydantic import ConfigDict


class Flashcard(BaseModel):
    question: str = Field(min_length=5, max_length=200)
    answer: str = Field(min_length=1, max_length=200)
    source_chunk: int


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str
    source_chunk: int


class ChunkOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    flashcards: list[Flashcard] = Field(default_factory=list)
    quiz: list[QuizQuestion] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)


class Summary(BaseModel):
    bullets: list[str]
    brief_script: str


class Kit(BaseModel):
    id: str
    title: str
    summary: Summary
    flashcards: list[Flashcard]
    quiz: list[QuizQuestion]
    audio_path: str | None = None
