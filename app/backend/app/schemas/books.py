from pydantic import BaseModel


class BookResponse(BaseModel):
    id: int | None
    gutenberg_id : int | None
    title: str | None
    author: str | None
    language : str | None
    text: str | None
    word_count: int | None
    centrality_score: float | None
    image_url: str | None = None
    metadata: dict[str, str | int | float] | None = None


