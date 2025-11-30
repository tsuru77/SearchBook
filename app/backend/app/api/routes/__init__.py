from fastapi import APIRouter

from app.api.routes import books, search, suggestions
from app.core.config import settings

api_router = APIRouter(prefix=settings.api_prefix)

api_router.include_router(search.router, tags=["search"])
api_router.include_router(books.router, tags=["books"])
api_router.include_router(suggestions.router, tags=["suggestions"])


