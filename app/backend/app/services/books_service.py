from fastapi import status
from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.schemas.books import BookResponse
from app.services.elasticsearch import get_elasticsearch_client


class BookServiceError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def get_book(book_id: str) -> BookResponse:
    client = get_elasticsearch_client()
    try:
        doc = await run_in_threadpool(
            client.get,
            index=settings.elasticsearch_index,
            id=book_id,
        )
    except Exception as exc:  # noqa: BLE001
        raise BookServiceError("Book not found", status.HTTP_404_NOT_FOUND) from exc

    source = doc.get("_source", {}) or {}
    return BookResponse(
        id=doc.get("_id"),
        title=source.get("title"),
        author=source.get("author"),
        text=source.get("text"),
        word_count=source.get("word_count"),
        centrality_score=source.get("centrality_score"),
        metadata=source.get("metadata", {}),
    )


