"""Search service using BM25 ranking with PostgreSQL."""

from typing import Any
from fastapi import status
from math import log
from collections import defaultdict
import re

from app.core.config import settings
from app.core.database import execute_query_all, execute_query_one
from app.schemas.search import SearchResponse, SearchResult, AdvancedSearchResponse


# debug
import datetime
from app.services import bm25
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
    try:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return SearchResponse(total=0, results=[])
        
        # --- OPTIMISATION 1 : Gestion du Tri Statique (Centralité) ---
        if sort_by == 'centrality':
            
            order_col = 'closeness_score'
            placeholders = ','.join(['%s'] * len(query_tokens))
            
            # 1. Requête SQL unique optimisée : Filtre, Jointure, Tri, Limite
            # - Jointure interne sur inverted_index pour filtrer les livres qui contiennent les mots-clés.
            # - GROUP BY pour s'assurer que chaque livre n'est retourné qu'une seule fois.
            # - ORDER BY la métrique statique (closeness_score) pour le classement.
            books_details = execute_query_all(
                f"""
                SELECT 
                    b.id, 
                    b.title, 
                    b.author, 
                    b.content AS text, 
                    b.closeness_score,
                    b.image_url,
                    b.publication_year,
                    COUNT(ii.book_id) AS matching_term_count  -- Compter combien de mots de la requête sont présents
                FROM 
                    books b
                INNER JOIN 
                    inverted_index ii ON b.id = ii.book_id
                WHERE 
                    ii.word IN ({placeholders})
                GROUP BY 
                    b.id, b.title, b.author, b.content, b.closeness_score, b.image_url, b.publication_year
                ORDER BY 
                    {order_col} DESC, 
                    matching_term_count DESC -- Ajout d'un critère secondaire de départage
                LIMIT %s
                """,
                tuple(query_tokens) + (size,)
            )

            if not books_details:
                return SearchResponse(total=0, results=[])

            # 2. Formatter et Retourner les résultats
            results: list[SearchResult] = []
            for book in books_details:
                 snippet = book['text'][:280] if book['text'] else ""
                 
                 results.append(SearchResult(
                     id=str(book['id']),
                     title=book['title'],
                     author=book['author'],
                     score=0.0, # BM25 non calculé (la pertinence est implicite par la présence du mot-clé)
                     centrality_score=book.get('closeness_score'),
                     image_url=book.get('image_url'),
                     snippet=snippet,
                 ))
            
            return SearchResponse(total=len(results), results=results)

        # 2. On récupère toutes les occurrences des tokens de la requête dans l'index inversé
        occurences_books = execute_query_all(
            f"""
            SELECT
                ii.word, 
                ii.frequency, 
                b.id,
                b.word_count
            FROM inverted_index ii 
            JOIN books b ON ii.book_id = b.id 
            WHERE ii.word = ANY(%s)
            """,
            (query_tokens,)
        )

        rows = execute_query_all(
            f"""
            SELECT word, COUNT(*) AS doc_freq
            FROM inverted_index
            WHERE word = ANY(%s)
            GROUP BY word
            """,
            (query_tokens,)
        )


        if not occurences_books or not rows:
            return SearchResponse(total=0, results=[])
        # --- STRATÉGIE PAR DÉFAUT : Tri par Pertinence (BM25) ---
        stats = execute_query_one("SELECT COUNT(*) as N, AVG(word_count) as avgdl FROM books")
        # rajouter l'heure
        if not stats or stats['n'] == 0:
             return SearchResponse(total=0, results=[])
        
        N = stats['n']
        avgdl = float(stats['avgdl'] or 1) 

        # BM25 Constants
        k1 = 1.5
        b = 0.75
        bm25_model = bm25.BM25(N, avgdl, k1, b)
        
        docs = defaultdict(lambda: {
            "word_count": 0,
            "words": {},
        })

        doc_freqs = {row["word"]: row["doc_freq"] for row in rows}

        # 3. Calcul des Scores BM25
        for book in occurences_books:  # chaque row = RealDictRow(...)
            book_id = book["id"]
            word = book["word"]
            freq = book["frequency"]
            word_count = book["word_count"]
            docs[book_id]["word_count"] = word_count
            docs[book_id]["words"][word] = {
                "frequency": freq,
                "number_documents": doc_freqs.get(word, 0)
            }
        

        scores = {}
        for book_id, doc in docs.items():
            scores[book_id] = bm25_model.score_query(doc)


        # 4. Formatter et Retourner les résultats
        results: list[SearchResult] = []

        # 1. On prend les IDs des X meilleurs livres (triés par pertinence)
        # top_ids = [doc_id for doc_id, score in ranked_docs[:size]]
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # size = min(50, len(ranked))
        # top_ids = [book_id for book_id, _ in ranked[:size]]
        top_ids = [book_id for book_id, _ in ranked]
        placeholders = ", ".join(["%s"] * len(top_ids))

        taille_text = 280
        books_details = execute_query_all(
            f"""
            SELECT 
                id, 
                title, 
                author, 
                LEFT(content, {taille_text}) AS text, -- OPTIMISATION : PostgreSQL coupe ici
                image_url
            FROM books 
            WHERE id IN ({placeholders})
            """,
            tuple(top_ids)
        )


        for book in books_details:
            
            results.append(SearchResult(
                id=str(book['id']),
                title=book['title'],
                author=book['author'],
                score=scores.get(book['id'], 0.0), # BM25 non calculé (la pertinence est implicite par la présence du mot-clé)
                centrality_score=0.0,
                image_url=book.get('image_url', ''),
                snippet=book.get('text', '')
            ))
        # Tri décroissant par score BM25
        results.sort(key=lambda r: r.score, reverse=True)


        return SearchResponse(total=len(results), results=results)

    except Exception as exc:
        # ... (Gestion des erreurs) ...
        pass

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


