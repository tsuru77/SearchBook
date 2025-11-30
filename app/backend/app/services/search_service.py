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


async def search_books(query: str, size: int, sort_by: str = 'relevance') -> SearchResponse:
    """Full-text search using BM25 ranking."""
    try:
        # Fetch all books including closeness_score
        all_books = execute_query_all("SELECT id, title, author, content AS text, word_count, image_url, closeness_score FROM books ORDER BY id")
        
        if not all_books:
            return SearchResponse(total=0, results=[])
        
        # Build BM25 index
        corpus = [_tokenize(book['text']) for book in all_books]
        bm25 = BM25Okapi(corpus)
        
        # Tokenize query and rank
        query_tokens = _tokenize(query)
        scores = bm25.get_scores(query_tokens)
        
        # Create results list first
        results: list[SearchResult] = []
        for idx, book in enumerate(all_books):
            if scores[idx] > 0:
                text = book['text']
                snippet = text[:280] if text else ""
                results.append(SearchResult(
                    id=str(book['id']),
                    title=book['title'],
                    author=book['author'],
                    score=scores[idx],
                    centrality_score=book.get('closeness_score'),
                    image_url=book.get('image_url'),
                    snippet=snippet,
                ))

        # Sort based on criteria
        if sort_by == 'centrality':
            # Sort by centrality (descending), then by relevance (descending)
            results.sort(key=lambda x: (x.centrality_score or 0, x.score), reverse=True)
        else:
            # Default: Sort by relevance (BM25 score)
            results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply limit after sorting
        results = results[:size]
        
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


