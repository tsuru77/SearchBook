"""Books service for fetching book details from PostgreSQL."""

from fastapi import status

from app.core.database import execute_query, execute_query_one
from app.schemas.books import BookResponse


class BookServiceError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def get_book(book_id: str) -> BookResponse:
    """Fetch a single book by ID."""
    try:
        # Increment click count
        execute_query("SELECT increment_book_click(%s)", (int(book_id),), commit=True)

        book = execute_query_one(
            "SELECT id, title, author, content AS text, word_count, image_url FROM books WHERE id = %s",
            (int(book_id),)
        )
    except ValueError:
        raise BookServiceError("Invalid book ID", status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        raise BookServiceError(f"Database error: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
    
    if not book:
        raise BookServiceError("Book not found", status.HTTP_404_NOT_FOUND)
    
    return BookResponse(
        id=str(book['id']),
        title=book['title'],
        author=book['author'],
        text=book['text'],
        word_count=book['word_count'],
        centrality_score=None,
        image_url=book.get('image_url'),
        metadata={},
    )


