from pydantic import BaseModel


class Suggestion(BaseModel):
    id: str | None
    title: str | None
    author: str | None
    similarity: float | None
    image_url: str | None = None


class SuggestionsResponse(BaseModel):
    book_id: str
    results: list[Suggestion]


