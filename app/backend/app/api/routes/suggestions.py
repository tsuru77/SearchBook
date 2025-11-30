from fastapi import APIRouter, HTTPException, Query

from app.schemas.suggestions import SuggestionsResponse
from app.services import suggestions_service

router = APIRouter()


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    book_id: str = Query(description="Reference book identifier"),
    limit: int = Query(default=5, ge=1, le=20),
) -> SuggestionsResponse:
    try:
        return await suggestions_service.get_suggestions(book_id=book_id, limit=limit)
    except suggestions_service.SuggestionsServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


