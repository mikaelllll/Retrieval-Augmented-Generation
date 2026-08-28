import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    page_number: int
    position: int
    content: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_pages(
    pages: list[str], target_words: int = 220, overlap_words: int = 40
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    position = 0
    for page_number, raw_text in enumerate(pages, start=1):
        words = normalize(raw_text).split()
        if not words:
            continue
        step = max(target_words - overlap_words, 1)
        for start in range(0, len(words), step):
            content = " ".join(words[start : start + target_words])
            if len(content) < 40:
                continue
            chunks.append(TextChunk(page_number, position, content))
            position += 1
            if start + target_words >= len(words):
                break
    return chunks
