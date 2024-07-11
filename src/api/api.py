from fastapi import APIRouter

from .endpoints import release

api_router = APIRouter()
api_router.include_router(release.router, prefix="", tags=["release"])
