from pydantic import BaseModel


class BookResponse(BaseModel):
    id: str | None
    title: str | None
    author: str | None
    text: str | None
    word_count: int | None
    centrality_score: float | None
    metadata: dict[str, str | int | float] | None = None


