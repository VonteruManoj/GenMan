from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.api.v1.endpoints.requests.semantic_search import (
    ConnectorsRequest,
    DocumentsRequest,
    LanguagesRequest,
    SearchFilters,
    SearchRequest,
    SuggestionsRequest,
    SummarizeRequest,
    TagsRequest,
)
from src.api.v1.endpoints.responses.semantic_search import (
    ConnectorData,
    ConnectorsResponse,
    ConnectorTypeData,
    DocumentsResponse,
    LanguagesResponse,
    SearchResponse,
    SearchSuggestionsResponse,
    SemanticSearchData,
    SummarizeAnswerData,
    SummarizeAnswerResponse,
    TagsResponse,
)
from src.core.containers import Container
from src.exceptions.http import ValidationException
from src.middlewares.collect_audit_data_middleware import (
    collect_audit_data_middleware,
)
from src.schemas.endpoints.responses import BooleanResponse
from src.services.semantic_search import (
    SemanticSearchService,
    SummarizeAnswerService,
)

router = APIRouter()


@router.get(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    description="Search for most relevant content based on a query.",
    tags=["semantic-search"],
    dependencies=[Depends(collect_audit_data_middleware)],
)
@inject
async def search(
    request: SearchRequest = Depends(),
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    filters = SearchFilters.parse_obj(request.filters)

    result, error = semantic_search_service.search(
        search=request.search,
        org_id=request.org_id,
        deployment_id=request.deployment_id,
        limit=request.limit,
        sort_by=request.sort_by,
        filters=filters,
    )

    status = {}
    if error:
        status["error"] = True
        status["error_code"] = 2001
        status["message"] = "Partial results returned"

    return SearchResponse(
        **status,
        data=SemanticSearchData(
            analyticsId=result["analytics_id"], options=result["options"]
        ),
    )


@router.get(
    "/suggestions",
    response_model=SearchSuggestionsResponse,
    status_code=status.HTTP_200_OK,
    description="Get suggestion for search typeahead.",
    tags=["semantic-search"],
)
@inject
async def get_search_suggestions(
    request: SuggestionsRequest = Depends(),
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    filters = SearchFilters.parse_obj(request.filters)

    result = semantic_search_service.get_search_suggestions(
        search=request.search,
        org_id=request.org_id,
        deployment_id=request.deployment_id,
        limit=request.limit,
        filters=filters,
    )

    return SearchSuggestionsResponse(data=result)


@router.get(
    "/summarize",
    response_model=SummarizeAnswerResponse,
    status_code=status.HTTP_200_OK,
    description="Summarize most relevant content into a concrete answer.",
    tags=["summarize"],
)
@inject
async def summarize(
    request: SummarizeRequest = Depends(),
    summarize_service: SummarizeAnswerService = Depends(
        Provide[Container.summarize_answer_service]
    ),
):
    result = summarize_service.handle(
        query=request.query,
        org_id=request.org_id,
        deployment_id=request.deployment_id,
        options_id_list=request.options,
    )
    return SummarizeAnswerResponse(
        data=SummarizeAnswerData(
            answer=result["answer"], options=result["options"]
        )
    )


@router.get(
    "/tags",
    response_model=TagsResponse,
    status_code=status.HTTP_200_OK,
    description="Get tags.",
    tags=["semantic-search"],
)
@inject
async def get_tags(
    request: TagsRequest = Depends(),
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    result, meta = semantic_search_service.get_tags(
        org_id=request.org_id,
        with_meta=request.with_meta,
    )
    return TagsResponse(data=result, meta=meta)


@router.get(
    "/connectors",
    response_model=ConnectorsResponse,
    status_code=status.HTTP_200_OK,
    description="Get connectors.",
    tags=["semantic-search"],
)
@inject
async def get_connectors(
    request: ConnectorsRequest = Depends(),
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    if request.deployment_id is None:
        results = semantic_search_service.get_connectors(org_id=request.org_id)
    else:
        results = semantic_search_service.get_deployment_connectors(
            org_id=request.org_id, deployment_id=request.deployment_id
        )

    data = [
        ConnectorData(
            **{
                **r.dict(),
                "connectorType": ConnectorTypeData(**r.connector_type.dict()),
            }
        )
        for r in results
    ]
    return ConnectorsResponse(data=data)


@router.get(
    "/documents",
    response_model=DocumentsResponse,
    status_code=status.HTTP_200_OK,
    description="Get documents.",
    tags=["semantic-search"],
)
@inject
async def get_documents(
    request: DocumentsRequest = Depends(),
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    if request.org_id is None and request.connector_id is None:
        raise ValidationException(
            message="At least one 'orgId' or"
            " 'connectorId' must be provided.",
        )

    if (request.limit is None and request.offset is not None) or (
        request.limit is not None and request.offset is None
    ):
        raise ValidationException(
            message="Both 'limit' and 'offset' must be provided together.",
        )

    documents = semantic_search_service.get_documents(
        org_id=request.org_id,
        connector_id=request.connector_id,
        limit=request.limit,
        offset=request.offset,
    )
    return DocumentsResponse(
        data=documents,
    )


@router.get(
    "/languages",
    response_model=LanguagesResponse,
    status_code=status.HTTP_200_OK,
    description="Get languages in sources by OrgId.",
    tags=["semantic-search"],
)
@inject
async def get_languages(
    request: LanguagesRequest = Depends(),
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    result = semantic_search_service.get_languages(
        org_id=request.org_id,
    )

    return LanguagesResponse(data=result)


@router.get(
    "/deployments/{uuid}/has-documents",
    response_model=BooleanResponse,
    status_code=status.HTTP_200_OK,
    description="Return true if the deployment has documents.",
    tags=["semantic-search"],
    dependencies=[Depends(collect_audit_data_middleware)],
)
@inject
async def deployment_has_documents(
    uuid: str,
    semantic_search_service: SemanticSearchService = Depends(
        Provide[Container.semantic_search_service]
    ),
):
    return BooleanResponse(
        data=semantic_search_service.deployment_has_documents(
            deployment_id=uuid
        ),
    )
