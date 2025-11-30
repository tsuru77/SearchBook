from typing import Any

from elasticsearch import NotFoundError
from fastapi import status
from fastapi.concurrency import run_in_threadpool

from app.core.config import settings
from app.schemas.search import AdvancedSearchResponse, SearchResponse, SearchResult
from app.services.elasticsearch import get_elasticsearch_client


class SearchServiceError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def search_books(query: str, size: int) -> SearchResponse:
    client = get_elasticsearch_client()
    body: dict[str, Any] = {
        "size": size,
        "query": {
            "match": {
                "text": {
                    "query": query,
                    "operator": "and",
                }
            }
        },
    }
    try:
        response = await run_in_threadpool(
            client.search,
            index=settings.elasticsearch_index,
            body=body,
        )
    except NotFoundError as exc:
        raise SearchServiceError("Index not found. Run ingestion first.", status.HTTP_404_NOT_FOUND) from exc
    return _build_search_response(response)


async def regex_search(regex: str, size: int) -> AdvancedSearchResponse:
    client = get_elasticsearch_client()
    body: dict[str, Any] = {
        "size": size,
        "query": {
            "regexp": {
                "text": {
                    "value": regex,
                    "case_insensitive": True,
                }
            }
        },
    }
    try:
        response = await run_in_threadpool(
            client.search,
            index=settings.elasticsearch_index,
            body=body,
        )
    except NotFoundError as exc:
        raise SearchServiceError("Index not found. Run ingestion first.", status.HTTP_404_NOT_FOUND) from exc
    hits = _build_search_response(response)
    return AdvancedSearchResponse(**hits.model_dump(), regex=regex)


def _build_search_response(response: dict[str, Any]) -> SearchResponse:
    hits = response.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    results: list[SearchResult] = []
    for hit in hits.get("hits", []):
        source = hit.get("_source", {}) or {}
        results.append(
            SearchResult(
                id=hit.get("_id"),
                title=source.get("title"),
                author=source.get("author"),
                score=hit.get("_score"),
                centrality_score=source.get("centrality_score"),
                snippet=source.get("snippet") or source.get("text", "")[:280],
            )
        )
    return SearchResponse(total=total, results=results)


