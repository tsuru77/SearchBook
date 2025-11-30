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
        # Verify book exists
        book = execute_query_one("SELECT id FROM books WHERE id = %s", (int(book_id),))
        if not book:
            raise SuggestionsServiceError("Book not found", status.HTTP_404_NOT_FOUND)
        
        # Fetch similar books from similarity table (ordered by rank)
        similar = execute_query_all(
            """
            SELECT b.id, b.title, b.author, sb.similarity_score
            FROM similar_books sb
            JOIN books b ON b.id = sb.similar_book_id
            WHERE sb.book_id = %s
            ORDER BY sb.rank ASC
            LIMIT %s
            """,
            (int(book_id), limit)
        )
        
        suggestions = [
            Suggestion(
                id=str(row['id']),
                title=row['title'],
                author=row['author'],
                similarity=row['similarity_score'],
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


