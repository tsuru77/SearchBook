"""Search service using BM25 ranking with PostgreSQL."""

from typing import Any
from fastapi import status
from math import log
from collections import defaultdict
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
    """Full-text search using manual BM25 ranking via Database."""
    try:
        # 1. Tokenize query
        query_tokens = _tokenize(query)
        if not query_tokens:
            return SearchResponse(total=0, results=[])

        # 2. Get Global Stats (N, avgdl)
        # N: Total number of documents
        # avgdl: Average document length
        stats = execute_query_one("SELECT COUNT(*) as N, AVG(word_count) as avgdl FROM books")
        if not stats or stats['n'] == 0:
             return SearchResponse(total=0, results=[])
        
        N = stats['n']
        avgdl = float(stats['avgdl'] or 1)  # Avoid division by zero

        # BM25 Constants
        k1 = 1.5
        b = 0.75

        # 3. Calculate Scores
        # Score(D,Q) = sum( IDF(q) * (f(q,D) * (k1 + 1)) / (f(q,D) + k1 * (1 - b + b * |D|/avgdl)) )
        
        doc_scores = defaultdict(float)
        
        for token in query_tokens:
            # Fetch posting list for this token: book_id, frequency, and book's word_count
            # We join with books to get word_count efficiently
            rows = execute_query_all(
                """
                SELECT ii.book_id, ii.frequency, b.word_count 
                FROM inverted_index ii 
                JOIN books b ON ii.book_id = b.id 
                WHERE ii.word = %s
                """, 
                (token,)
            )
            
            n_q = len(rows) # Number of documents containing the term
            if n_q == 0:
                continue

            # Calculate IDF for this term
            # IDF(q) = log( (N - n(q) + 0.5) / (n(q) + 0.5) + 1 )
            idf = log((N - n_q + 0.5) / (n_q + 0.5) + 1)
            
            for row in rows:
                book_id = row['book_id']
                freq = row['frequency']
                doc_len = row['word_count']
                
                # Calculate term score
                numerator = freq * (k1 + 1)
                denominator = freq + k1 * (1 - b + b * (doc_len / avgdl))
                term_score = idf * (numerator / denominator)
                
                doc_scores[book_id] += term_score

        if not doc_scores:
            return SearchResponse(total=0, results=[])

        # 4. Sort and Pagination
        # Convert to list of (book_id, score)
        ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # We need to fetch details for the top results to return them
        # Note: If sort_by is centrality, we might need to fetch more or re-sort.
        # For efficiency, let's fetch details for ALL scored docs if the set is small, 
        # or just the top K if we are only sorting by relevance.
        # However, the user requirement says "sort by relevance OR centrality".
        # If centrality, we need the centrality scores for these docs.
        
        top_ids = [doc_id for doc_id, _ in ranked_docs]
        
        if not top_ids:
             return SearchResponse(total=0, results=[])

        # Fetch details for all candidates (or a reasonable batch if too many)
        # For now, let's fetch all matching docs to allow proper sorting by centrality
        # In a real huge system, we'd only fetch top K, but here we need to support re-sorting.
        
        placeholders = ','.join(['%s'] * len(top_ids))
        books_details = execute_query_all(
            f"SELECT id, title, author, content AS text, word_count, image_url, closeness_score FROM books WHERE id IN ({placeholders})",
            tuple(top_ids)
        )
        
        # Create a lookup for details
        books_map = {b['id']: b for b in books_details}
        
        results: list[SearchResult] = []
        for doc_id, score in ranked_docs:
            if doc_id not in books_map:
                continue
            book = books_map[doc_id]
            text = book['text']
            snippet = text[:280] if text else ""
            
            results.append(SearchResult(
                id=str(book['id']),
                title=book['title'],
                author=book['author'],
                score=score,
                centrality_score=book.get('closeness_score'),
                image_url=book.get('image_url'),
                snippet=snippet,
            ))

        # Sort based on criteria
        if sort_by == 'centrality':
            # Sort by centrality (descending), then by relevance (descending)
            results.sort(key=lambda x: (x.centrality_score or 0, x.score), reverse=True)
        else:
            # Default: Sort by relevance (BM25 score) - already sorted by construction, but good to ensure
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


