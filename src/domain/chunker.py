def _token_count(text: str) -> int:
    try:
        import tiktoken
        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except ImportError:
        return len(text.split())


def chunk_text(text: str, max_tokens: int = 1500) -> list[str]:
    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for paragraph in paragraphs or [text.strip()]:
        paragraph_tokens = _token_count(paragraph)
        if current and current_tokens + paragraph_tokens > max_tokens:
            chunks.append("\n\n".join(current))
            current, current_tokens = [], 0
        if paragraph_tokens <= max_tokens:
            current.append(paragraph)
            current_tokens += paragraph_tokens
            continue
        words = paragraph.split()
        part_words: list[str] = []
        for word in words:
            candidate = " ".join(part_words + [word])
            if part_words and _token_count(candidate) > max_tokens:
                if current:
                    chunks.append("\n\n".join(current))
                    current, current_tokens = [], 0
                chunks.append(" ".join(part_words))
                part_words = [word]
            else:
                part_words.append(word)
        if part_words:
            if current and current_tokens + _token_count(" ".join(part_words)) <= max_tokens:
                current.append(" ".join(part_words))
            else:
                if current:
                    chunks.append("\n\n".join(current))
                    current, current_tokens = [], 0
                chunks.append(" ".join(part_words))
    if current:
        chunks.append("\n\n".join(current))
    return chunks
