"""Routes de recherche simple."""
import time
from fastapi import APIRouter, HTTPException, Query
from app.models import SearchRequest, SearchResponse, ErrorResponse
from app.services import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("/simple", response_model=SearchResponse)
async def simple_search(request: SearchRequest):
    """
    Recherche simple par mot-clé.
    
    Query: Terme à chercher
    ranking_by: Critère de classement ('occurrences' ou 'pagerank')
    limit: Nombre maximal de résultats (défaut: 20)
    """
    try:
        start_time = time.time()
        
        # Valider ranking_by
        if request.ranking_by not in ["occurrences", "pagerank"]:
            raise HTTPException(
                status_code=400,
                detail="ranking_by doit être 'occurrences' ou 'pagerank'"
            )
        
        # Effectuer la recherche
        results, total_count = SearchService.simple_search(
            query=request.query,
            ranking_by=request.ranking_by,
            limit=request.limit
        )
        
        # Récupérer les suggestions (top 3 résultats)
        top_doc_ids = [r.doc_id for r in results[:3]]
        suggestions = SearchService.get_suggestions(top_doc_ids, limit=10)
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return SearchResponse(
            query=request.query,
            ranking_by=request.ranking_by,
            total_results=total_count,
            results=results,
            suggestions=suggestions,
            execution_time_ms=execution_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(
    regex_pattern: str = Query(..., min_length=1, max_length=200),
    ranking_by: str = Query(default="occurrences"),
    limit: int = Query(default=20, ge=1, le=100)
):
    """
    Recherche avancée par expression régulière.
    
    regex_pattern: Pattern regex (ex: '^the.*ing$')
    ranking_by: Critère de classement ('occurrences' ou 'pagerank')
    limit: Nombre maximal de résultats (défaut: 20)
    """
    try:
        start_time = time.time()
        
        # Valider ranking_by
        if ranking_by not in ["occurrences", "pagerank"]:
            raise HTTPException(
                status_code=400,
                detail="ranking_by doit être 'occurrences' ou 'pagerank'"
            )
        
        # Effectuer la recherche
        results, total_count = SearchService.advanced_search(
            regex_pattern=regex_pattern,
            ranking_by=ranking_by,
            limit=limit
        )
        
        # Récupérer les suggestions (top 3 résultats)
        top_doc_ids = [r.doc_id for r in results[:3]]
        suggestions = SearchService.get_suggestions(top_doc_ids, limit=10)
        
        execution_time = (time.time() - start_time) * 1000  # ms
        
        return SearchResponse(
            query=regex_pattern,
            ranking_by=ranking_by,
            total_results=total_count,
            results=results,
            suggestions=suggestions,
            execution_time_ms=execution_time
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
