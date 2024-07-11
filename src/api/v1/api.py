from fastapi import APIRouter

from src.api.v1.endpoints import authoring, health, semantic_search
from src.api.v1.endpoints.analytics.api import router as analytics_router

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(
    authoring.router, prefix="/authoring", tags=["authoring"]
)
api_router.include_router(
    semantic_search.router, prefix="/semantic-search", tags=["semantic-search"]
)
api_router.include_router(
    analytics_router, prefix="/analytics", tags=["analytics"]
)
