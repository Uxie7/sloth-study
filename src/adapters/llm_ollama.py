import json
from typing import TypeVar
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from src.config import settings
from src.domain.schemas import ChunkOutput


def _repair_chunk_payload(payload: dict) -> dict:
    if not isinstance(payload, dict) or "quiz" not in payload:
        return payload
    repaired_quiz = []
    for item in payload.get("quiz") or []:
        if not isinstance(item, dict):
            continue
        options = [str(option) for option in item.get("options") or []]
        options = (options + ["Not stated in the source", "None of these", "An unrelated example", "Not applicable"])[:4]
        repaired_quiz.append({
            **item,
            "options": options,
            "correct_index": max(0, min(int(item.get("correct_index", 0)), 3)),
            "explanation": str(item.get("explanation", "The selected answer is grounded in the source.")),
            "source_chunk": int(item.get("source_chunk", 0)),
        })
    return {**payload, "quiz": repaired_quiz}

T = TypeVar("T", bound=BaseModel)


class OllamaLLM:
    def __init__(self, client=None):
        self.client = client or OpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )

    def generate_json(self, prompt: str, schema: type[T]) -> T:
        last_error: Exception | None = None
        for attempt in range(2):
            response = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            try:
                payload = json.loads(response.choices[0].message.content or "")
                if schema is ChunkOutput:
                    payload = _repair_chunk_payload(payload)
                return schema.model_validate(payload)
            except (json.JSONDecodeError, ValidationError) as error:
                last_error = error
                prompt += f"\nPrevious response failed validation: {error}. Return valid JSON only."
        raise ValueError("LLM returned invalid JSON after one retry") from last_error
