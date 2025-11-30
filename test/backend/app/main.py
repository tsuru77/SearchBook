"""
FastAPI application main file.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.db import initialize_pool, close_pool
from app.api.routes.search import router as search_router

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SearchBook API",
    description="Moteur de recherche pour bibliothèque avec Jaccard et PageRank",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Événements ====================

@app.on_event("startup")
async def startup_event():
    """Initialiser le pool de connexions DB à la démarrage."""
    logger.info("🚀 Démarrage de SearchBook API...")
    initialize_pool(minconn=2, maxconn=20)
    logger.info("✅ Pool de connexions PostgreSQL initialisé")

@app.on_event("shutdown")
async def shutdown_event():
    """Fermer le pool de connexions DB à l'arrêt."""
    logger.info("🛑 Arrêt de SearchBook API...")
    close_pool()
    logger.info("✅ Pool de connexions fermé")

# ==================== Routes ====================

app.include_router(search_router)

@app.get("/", tags=["root"])
async def root():
    """Endpoint racine."""
    return {
        "message": "Bienvenue sur SearchBook API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

# ==================== Error handlers ====================

@app.get("/api/search/simple")
async def simple_search_get():
    """Redirect to POST endpoint with documentation."""
    return {
        "error": "Utilisez POST /api/search/simple avec un JSON body",
        "example": {
            "query": "book",
            "ranking_by": "occurrences",
            "limit": 20
        }
    }
