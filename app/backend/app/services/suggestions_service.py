"""Suggestions service for finding similar books based on Jaccard similarity."""

from typing import Any
from fastapi import status

from app.core.config import settings
from app.core.database import execute_query_all, execute_query_one
from app.schemas.suggestions import Suggestion, SuggestionsResponse


class SuggestionsServiceError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def get_suggestions(book_id: str, limit: int) -> SuggestionsResponse:
    """Get similar books based on Jaccard similarity."""
    try:
        # Verify book exists (unless requesting general suggestions with id=0)
        if int(book_id) != 0:
            book = execute_query_one("SELECT id FROM books WHERE id = %s", (int(book_id),))
            if not book:
                raise SuggestionsServiceError("Book not found", status.HTTP_404_NOT_FOUND)
        
        # Fetch similar books using stored procedure (returns popular books)
        similar = execute_query_all(
            "SELECT * FROM get_suggestions(%s, %s)",
            (int(book_id), limit)
        )
        
        suggestions = [
            Suggestion(
                id=str(row['similar_book_id']),
                title=row['title'],
                author=row['author'],
                similarity=float(row['similarity_score']), # This is now click_count
                image_url=row['image_url'],
            )
            for row in similar
        ]
        
        return SuggestionsResponse(book_id=book_id, results=suggestions)
    
    except ValueError:
        raise SuggestionsServiceError("Invalid book ID", status.HTTP_400_BAD_REQUEST)
    except SuggestionsServiceError:
        raise
    except Exception as exc:
        raise SuggestionsServiceError(f"Database error: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc


