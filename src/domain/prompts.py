import json


def chunk_prompt(chunk: str, idx: int) -> str:
    return f"""Create study material from only the source text below. Do not invent facts.
Return only a JSON object with exactly these top-level keys: "flashcards", "quiz", and "key_points".
Each flashcard object must have exactly: "question", "answer", and "source_chunk".
Each quiz object must have exactly: "question", "options", "correct_index", "explanation", and "source_chunk".
Create at least 10 flashcards and 5 quiz questions when the source contains enough material.
The "options" array must contain exactly four strings. Use source_chunk {idx} for every item.
Example shape: {{"flashcards": [{{"question": "What is X?", "answer": "Y", "source_chunk": {idx}}}], "quiz": [{{"question": "Which?", "options": ["A", "B", "C", "D"], "correct_index": 0, "explanation": "A.", "source_chunk": {idx}}}], "key_points": ["X is Y"]}}

Source text:
{chunk}
"""


def summary_prompt(key_points: list[str]) -> str:
    return f"""Create a concise revision summary from these grounded key points:
{json.dumps(key_points)}
Return only a JSON object with exactly these top-level keys: "bullets" and "brief_script".
"bullets" must be an array of strings. "brief_script" must be a spoken-language string,
without markdown or bullet symbols, and approximately 700 words.
Example shape: {{"bullets": ["Key point one"], "brief_script": "A spoken revision brief."}}"""
