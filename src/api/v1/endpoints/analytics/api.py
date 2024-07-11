from fastapi import APIRouter

from src.api.v1.endpoints.analytics.semantic_search import (
    router as semantic_search_router,
)

router = APIRouter()
router.include_router(
    semantic_search_router,
    prefix="/semantic-search",
    tags=["analytics", "semantic-search"],
)
