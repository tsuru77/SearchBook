from typing import Any

from fastapi import status
from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.schemas.suggestions import Suggestion, SuggestionsResponse
from app.services.elasticsearch import get_elasticsearch_client


class SuggestionsServiceError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def get_suggestions(book_id: str, limit: int) -> SuggestionsResponse:
    client = get_elasticsearch_client()
    try:
        doc = await run_in_threadpool(
            client.get,
            index=settings.elasticsearch_index,
            id=book_id,
        )
    except Exception as exc:  # noqa: BLE001
        raise SuggestionsServiceError("Book not found", status.HTTP_404_NOT_FOUND) from exc

    source = doc.get("_source", {}) or {}
    neighbors: list[dict[str, Any]] = source.get("similar_books", []) or []
    suggestions = [
        Suggestion(
            id=item.get("id"),
            title=item.get("title"),
            author=item.get("author"),
            similarity=item.get("similarity"),
        )
        for item in neighbors[:limit]
    ]
    return SuggestionsResponse(book_id=book_id, results=suggestions)


