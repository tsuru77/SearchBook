"""
Schémas Pydantic pour requêtes et réponses API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

# ==================== REQUÊTES ====================

class SearchRequest(BaseModel):
    """Requête de recherche simple."""
    query: str = Field(..., min_length=1, max_length=100)
    ranking_by: str = Field(
        default="occurrences",
        description="Critère de classement: 'occurrences' ou 'pagerank'"
    )
    limit: int = Field(default=20, ge=1, le=100)

class AdvancedSearchRequest(BaseModel):
    """Requête de recherche avancée par regex."""
    regex_pattern: str = Field(..., min_length=1, max_length=200)
    ranking_by: str = Field(
        default="occurrences",
        description="Critère de classement: 'occurrences' ou 'pagerank'"
    )
    limit: int = Field(default=20, ge=1, le=100)

# ==================== RÉPONSES ====================

class DocumentResult(BaseModel):
    """Résultat de document trouvé."""
    doc_id: UUID
    title: str
    author: Optional[str] = None
    word_count: Optional[int] = None
    occurrences: int = Field(..., description="Occurrences du terme/pattern")
    pagerank_score: Optional[float] = Field(None, description="Score PageRank")
    ranking_position: int = Field(..., description="Position dans le classement")

class SuggestionResult(BaseModel):
    """Suggestion basée sur graphe Jaccard."""
    doc_id: UUID
    title: str
    author: Optional[str] = None
    jaccard_score: float = Field(..., description="Score de similarité Jaccard")

class SearchResponse(BaseModel):
    """Réponse complète d'une recherche."""
    query: str
    ranking_by: str
    total_results: int
    results: List[DocumentResult] = Field(default_factory=list)
    suggestions: List[SuggestionResult] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None

class ErrorResponse(BaseModel):
    """Réponse en cas d'erreur."""
    error: str
    detail: Optional[str] = None
