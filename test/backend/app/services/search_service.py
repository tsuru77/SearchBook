"""
Service de recherche : logique pour recherche simple, avancée, classement et suggestions.
"""
import re
from typing import List, Tuple
from uuid import UUID
from app.db import get_db_cursor
from app.models.schemas import DocumentResult, SuggestionResult

class SearchService:
    """Service de recherche dans la base de données."""
    
    @staticmethod
    def simple_search(query: str, ranking_by: str = "occurrences", limit: int = 20) -> Tuple[List[DocumentResult], int]:
        """
        Recherche simple par mot-clé.
        
        Args:
            query: Terme à chercher
            ranking_by: 'occurrences' ou 'pagerank'
            limit: Nombre maximal de résultats
            
        Returns:
            (liste de DocumentResult, total_results)
        """
        with get_db_cursor() as cur:
            # Déterminer l'ordre de tri
            order_clause = "ii.occurrences DESC" if ranking_by == "occurrences" else "cs.pagerank_score DESC"
            
            # Requête: recherche simple + join avec PageRank
            # NOTE: Plus besoin de JOIN terms - term est directement dans inverted_index
            query_sql = f"""
                SELECT 
                    d.id, d.title, d.author, d.word_count,
                    ii.occurrences, cs.pagerank_score,
                    ROW_NUMBER() OVER (ORDER BY {order_clause}) as pos
                FROM inverted_index ii
                JOIN documents d ON d.id = ii.doc_id
                LEFT JOIN centrality_scores cs ON cs.doc_id = d.id
                WHERE LOWER(ii.term) = LOWER(%s)
                ORDER BY {order_clause}
                LIMIT %s
            """
            
            cur.execute(query_sql, (query, limit))
            rows = cur.fetchall()
            
            # Compter le total (avant LIMIT)
            count_sql = """
                SELECT COUNT(DISTINCT d.id)
                FROM inverted_index ii
                JOIN documents d ON d.id = ii.doc_id
                WHERE LOWER(ii.term) = LOWER(%s)
            """
            cur.execute(count_sql, (query,))
            total_count = cur.fetchone()[0]
            
            results = [
                DocumentResult(
                    doc_id=UUID(row[0]),
                    title=row[1],
                    author=row[2],
                    word_count=row[3],
                    occurrences=row[4],
                    pagerank_score=row[5],
                    ranking_position=int(row[6])
                )
                for row in rows
            ]
            
            return results, total_count
    
    @staticmethod
    def advanced_search(regex_pattern: str, ranking_by: str = "occurrences", limit: int = 20) -> Tuple[List[DocumentResult], int]:
        """
        Recherche avancée par expression régulière.
        
        Args:
            regex_pattern: Pattern regex (ex: '^the.*ing$')
            ranking_by: 'occurrences' ou 'pagerank'
            limit: Nombre maximal de résultats
            
        Returns:
            (liste de DocumentResult, total_results)
        """
        with get_db_cursor() as cur:
            # Valider la regex
            try:
                re.compile(regex_pattern)
            except re.error as e:
                raise ValueError(f"Regex invalide: {e}")
            
            order_clause = "ii.occurrences DESC" if ranking_by == "occurrences" else "cs.pagerank_score DESC"
            
            # NOTE: Plus besoin de JOIN terms - term est directement dans inverted_index
            query_sql = f"""
                SELECT 
                    d.id, d.title, d.author, d.word_count,
                    ii.occurrences, cs.pagerank_score,
                    ROW_NUMBER() OVER (ORDER BY {order_clause}) as pos
                FROM inverted_index ii
                JOIN documents d ON d.id = ii.doc_id
                LEFT JOIN centrality_scores cs ON cs.doc_id = d.id
                WHERE ii.term ~ %s
                ORDER BY {order_clause}
                LIMIT %s
            """
            
            cur.execute(query_sql, (regex_pattern, limit))
            rows = cur.fetchall()
            
            # Compter le total
            count_sql = """
                SELECT COUNT(DISTINCT d.id)
                FROM inverted_index ii
                JOIN documents d ON d.id = ii.doc_id
                WHERE ii.term ~ %s
            """
            cur.execute(count_sql, (regex_pattern,))
            total_count = cur.fetchone()[0]
            
            results = [
                DocumentResult(
                    doc_id=UUID(row[0]),
                    title=row[1],
                    author=row[2],
                    word_count=row[3],
                    occurrences=row[4],
                    pagerank_score=row[5],
                    ranking_position=int(row[6])
                )
                for row in rows
            ]
            
            return results, total_count
    
    @staticmethod
    def get_suggestions(doc_ids: List[UUID], limit: int = 10, use_popularity: bool = False) -> List[SuggestionResult]:
        """
        Retourne les suggestions (voisins Jaccard) pour une liste de documents.
        
        Args:
            doc_ids: Liste de doc_id (les plus pertinents de la recherche)
            limit: Nombre maximal de suggestions
            use_popularity: Si True, filtre par clicks (popularity_doc)
            
        Returns:
            Liste de SuggestionResult
        """
        if not doc_ids:
            return []
        
        with get_db_cursor() as cur:
            # Collecter les voisins Jaccard des documents principaux
            placeholders = ','.join(['%s'] * len(doc_ids))
            doc_ids_str = [str(d) for d in doc_ids]
            
            query_sql = f"""
                SELECT DISTINCT
                    d.id, d.title, d.author, je.jaccard_score
                FROM jaccard_edges je
                JOIN documents d ON 
                    (je.doc_a = d.id AND je.doc_b = ANY(ARRAY[{placeholders}]::uuid[]))
                    OR (je.doc_b = d.id AND je.doc_a = ANY(ARRAY[{placeholders}]::uuid[]))
                LEFT JOIN popularity_doc pd ON pd.doc_id = d.id
                ORDER BY je.jaccard_score DESC, COALESCE(pd.clicks, 0) DESC
                LIMIT %s
            """
            
            cur.execute(query_sql, doc_ids_str + doc_ids_str + [limit])
            rows = cur.fetchall()
            
            suggestions = [
                SuggestionResult(
                    doc_id=UUID(row[0]),
                    title=row[1],
                    author=row[2],
                    jaccard_score=row[3]
                )
                for row in rows
            ]
            
            return suggestions
    
    @staticmethod
    def track_click(doc_id: UUID) -> None:
        """Incrémente le compteur de clics pour un document."""
        with get_db_cursor() as cur:
            cur.execute("""
                INSERT INTO popularity_doc (doc_id, clicks, last_clicked)
                VALUES (%s, 1, now())
                ON CONFLICT (doc_id) DO UPDATE
                SET clicks = popularity_doc.clicks + 1, last_clicked = now()
            """, (str(doc_id),))
