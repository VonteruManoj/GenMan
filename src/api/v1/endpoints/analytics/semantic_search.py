from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

import src.repositories.models.analytics.semantic_search_analytics_repository as ssar  # noqa: E501
from src.api.v1.endpoints.analytics.requests.semantic_search import (
    AppendEventToBatchRequest,
    UpdateBatchRequest,
)
from src.core.containers import Container
from src.exceptions.http import NotFoundException
from src.middlewares.collect_audit_data_middleware import (
    collect_audit_data_middleware,
)
from src.schemas.endpoints.responses import BaseResponse

router = APIRouter()


@router.patch(
    "/{uuid}",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="Update analytics batch.",
    tags=["analytics", "semantic-search"],
    dependencies=[Depends(collect_audit_data_middleware)],
)
@inject
async def update_batch(
    uuid: str,
    request: UpdateBatchRequest,
    semantic_search_analytics_repository: ssar.SemanticSearchAnalyticsRepository = Depends(  # noqa: E501
        Provide[Container.semantic_search_analytics_repository]
    ),
):
    batch = semantic_search_analytics_repository.find_batch_by_id(uuid)

    if not batch:
        raise NotFoundException(message="Batch not found")

    semantic_search_analytics_repository.update_batch(
        batch=batch,
        current_deployment_type=request.currentDeploymentType,
        location=request.location,
        previous_session_id=request.previousSessionId,
    )

    return BaseResponse(
        message="Batch updated successfully",
        data=None,
    )


@router.post(
    "/{uuid}",
    response_model=BaseResponse,
    status_code=status.HTTP_200_OK,
    description="Append event to analytics batch.",
    tags=["analytics", "semantic-search"],
    dependencies=[Depends(collect_audit_data_middleware)],
)
@inject
async def append_event_to_batch(
    uuid: str,
    request: AppendEventToBatchRequest,
    semantic_search_analytics_repository: ssar.SemanticSearchAnalyticsRepository = Depends(  # noqa: E501
        Provide[Container.semantic_search_analytics_repository]
    ),
):
    batch = semantic_search_analytics_repository.find_batch_by_id(uuid)

    if not batch:
        raise NotFoundException(message="Batch not found")

    semantic_search_analytics_repository.append_event_to_batch(
        batch=batch,
        operation=request.operation,
        message=request.message,
        data=request.data,
    )

    return BaseResponse(
        message="Event appended to batch successfully",
        data=None,
    )
