from typing import Any

from fastapi import APIRouter, status

from src.core.config import get_settings

from .responses.health import HealthData, HealthResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    description="Retrieve service health check",
    tags=["health"],
)
def get_health() -> Any:
    """
    Retrieve service health check.
    """
    data = HealthData(
        status="ok",
        version="v1",
        release=get_settings().RELEASE_STRING,
    )

    return HealthResponse(data=data)
