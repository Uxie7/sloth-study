import json


def chunk_prompt(chunk: str, idx: int) -> str:
    return f"""Create study material from only the source text below. Do not invent facts.
Return JSON with flashcards, quiz, and key_points. Each flashcard must contain one short fact.
Quiz questions must have exactly four options and one correct_index from 0 to 3.
Use source_chunk {idx} for every generated item.

Source text:
{chunk}
"""


def summary_prompt(key_points: list[str]) -> str:
    return f"""Create a concise revision summary from these grounded key points:
{json.dumps(key_points)}
Return JSON with bullets and a brief_script. The brief_script should be spoken language,
without markdown or bullet symbols, and approximately 700 words."""
