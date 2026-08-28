from app.services.chunking import chunk_pages, normalize


def test_normalize_collapses_whitespace() -> None:
    assert normalize("alpha\n  beta\t gamma") == "alpha beta gamma"


def test_chunk_pages_preserves_page_and_overlap() -> None:
    pages = [" ".join(f"word-{index}" for index in range(500))]
    chunks = chunk_pages(pages, target_words=100, overlap_words=20)
    assert len(chunks) == 6
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert chunks[0].content.split()[-20:] == chunks[1].content.split()[:20]


def test_chunk_pages_ignores_empty_pages() -> None:
    assert chunk_pages(["", " \n "]) == []

