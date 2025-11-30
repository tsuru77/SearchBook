from pydantic import BaseModel


class SearchResult(BaseModel):
    id: str | None
    title: str | None
    author: str | None
    score: float | None
    centrality_score: float | None
    image_url: str | None = None
    snippet: str | None


class SearchResponse(BaseModel):
    total: int
    results: list[SearchResult]


class AdvancedSearchResponse(SearchResponse):
    regex: str


