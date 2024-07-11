import json

from pydantic import BaseModel, Field, Json


class AppendEventToBatchRequest(BaseModel):
    operation: str = Field(
        default=...,
        description="The operation performed.",
    )
    message: str = Field(
        default=None,
        description="A message to be appended.",
    )
    data: Json = Field(
        default=None,
        description="Extra data.",
    )

    class Config:
        schema_extra = {
            "example": {
                "operation": "user_click",
                "message": "User click in a result.",
                "data": json.dumps(
                    {
                        "link": "http://example.com",
                        "node_id": 1,
                        "project_id": 1,
                        "result_order": 2,
                        "sort_by": "relevance",
                    }
                ),
            }
        }


class UpdateBatchRequest(BaseModel):
    currentDeploymentType: str = Field(default=None)
    location: str = Field(default=None)
    previousSessionId: str = Field(default=None)
