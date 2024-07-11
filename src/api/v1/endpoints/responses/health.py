from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.endpoints.responses import BaseResponse


class HealthData(BaseModel):
    status: str = Field(
        default=..., description="Indicates the service status."
    )
    version: Optional[str] = Field(
        default=None, description="The version of the service."
    )
    release: Optional[str] = Field(
        default=None, description="The current build release."
    )


class HealthResponse(BaseResponse):
    data: HealthData
