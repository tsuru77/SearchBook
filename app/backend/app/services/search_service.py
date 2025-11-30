"""Search service using BM25 ranking with PostgreSQL."""

from typing import Any
from fastapi import status
from rank_bm25 import BM25Okapi
import re

from app.core.config import settings
from app.core.database import execute_query_all, execute_query_one
from app.schemas.search import SearchResponse, SearchResult, AdvancedSearchResponse


class SearchServiceError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _tokenize(text: str) -> list[str]:
    """Simple tokenization for BM25."""
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens


async def search_books(query: str, size: int) -> SearchResponse:
    """Full-text search using BM25 ranking."""
    try:
        # Fetch all books
        all_books = execute_query_all("SELECT id, title, author, content AS text, word_count, image_url FROM books ORDER BY id")
        
        if not all_books:
            return SearchResponse(total=0, results=[])
        
        # Build BM25 index
        corpus = [_tokenize(book['text']) for book in all_books]
        bm25 = BM25Okapi(corpus)
        
        # Tokenize query and rank
        query_tokens = _tokenize(query)
        scores = bm25.get_scores(query_tokens)
        
        # Create ranked results
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        results: list[SearchResult] = []
        for idx in ranked_indices[:size]:
            if scores[idx] > 0:  # Only include books with non-zero score
                book = all_books[idx]
                text = book['text']
                snippet = text[:280] if text else ""
                
                results.append(SearchResult(
                    id=str(book['id']),
                    title=book['title'],
                    author=book['author'],
                    score=scores[idx],
                    centrality_score=None,
                    image_url=book.get('image_url'),
                    snippet=snippet,
                ))
        
        return SearchResponse(total=len(results), results=results)
    
    except Exception as exc:
        raise SearchServiceError(f"Search failed: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc


async def regex_search(regex: str, size: int) -> AdvancedSearchResponse:
    """Advanced search using regex."""
    try:
        # Compile regex
        pattern = re.compile(regex, re.IGNORECASE)
        
        # Fetch all books
        all_books = execute_query_all("SELECT id, title, author, content AS text, word_count, image_url FROM books ORDER BY id")
        
        results: list[SearchResult] = []
        for book in all_books:
            text = book['text']
            if pattern.search(text):
                snippet = text[:280] if text else ""
                results.append(SearchResult(
                    id=str(book['id']),
                    title=book['title'],
                    author=book['author'],
                    score=None,
                    centrality_score=None,
                    image_url=book.get('image_url'),
                    snippet=snippet,
                ))
                if len(results) >= size:
                    break
        
        return AdvancedSearchResponse(total=len(results), results=results, regex=regex)
    
    except re.error as exc:
        raise SearchServiceError(f"Invalid regex: {str(exc)}", status.HTTP_400_BAD_REQUEST) from exc
    except Exception as exc:
        raise SearchServiceError(f"Regex search failed: {str(exc)}", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc


