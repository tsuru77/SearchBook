from fastapi import APIRouter, HTTPException, Query

from app.schemas.search import AdvancedSearchResponse, SearchResponse
from app.services import search_service

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_books(
    query: str = Query(min_length=1, description="Full-text query string"),
    size: int = Query(default=10, ge=1, le=50),
) -> SearchResponse:
    try:
        return await search_service.search_books(query=query, size=size)
    except search_service.SearchServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/search/advanced", response_model=AdvancedSearchResponse)
async def regex_search_books(
    regex: str = Query(min_length=2, description="Elasticsearch-compatible regular expression"),
    size: int = Query(default=10, ge=1, le=50),
) -> AdvancedSearchResponse:
    try:
        return await search_service.regex_search(regex=regex, size=size)
    except search_service.SearchServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


