import json
from typing import TypeVar
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from src.config import settings

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
                return schema.model_validate(payload)
            except (json.JSONDecodeError, ValidationError) as error:
                last_error = error
                prompt += f"\nPrevious response failed validation: {error}. Return valid JSON only."
        raise ValueError("LLM returned invalid JSON after one retry") from last_error
