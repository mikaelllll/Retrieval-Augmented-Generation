from functools import lru_cache

from fastembed import TextEmbedding

from app.config import settings


@lru_cache(maxsize=1)
def model() -> TextEmbedding:
    return TextEmbedding(model_name=settings.embedding_model)


def embed_passages(texts: list[str]) -> list[list[float]]:
    return [vector.tolist() for vector in model().embed(texts)]


def embed_query(text: str) -> list[float]:
    return next(model().query_embed(text)).tolist()
