from fastapi import APIRouter, HTTPException, Path

from app.schemas.books import BookResponse
from app.services import books_service

router = APIRouter()


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str = Path(description="Book ID from database"),
) -> BookResponse:
    try:
        return await books_service.get_book(book_id=book_id)
    except books_service.BookServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


