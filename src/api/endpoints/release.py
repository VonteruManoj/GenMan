from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

from src.core.config import get_settings

router = APIRouter()


@router.get(
    "/release",
    status_code=status.HTTP_200_OK,
    description="Retrieve the current build release.",
    tags=["release"],
    response_class=HTMLResponse,
)
def get_release() -> Any:
    """
    Retrieve the current build release.
    """
    return get_settings().RELEASE_STRING
