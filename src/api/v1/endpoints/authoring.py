from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.chain.chain import ChainResolver
from src.contracts.repositories.assets import AssetsRepositoryInterface
from src.core.containers import Container
from src.repositories.audit import AuditInMemoryRepository
from src.repositories.models.usage_log_repository import UsageLogRepository
from src.schemas.endpoints.responses import PaginationResponseMeta
from src.services.authoring import (
    ChangeToneService,
    ExpandWritingService,
    FixGrammarAuthoringService,
    ImproveWritingService,
    ReduceReadingComplexityService,
    ReduceReadingTimeService,
    SummarizeIntoStepsService,
    SummarizeService,
    TranslateService,
)
from src.services.moderation import ModerationCheckOrFailService

from .requests.authoring import (
    ChangeToneRequest,
    ExpandWritingRequest,
    FixGrammarRequest,
    ImproveWritingRequest,
    ReduceReadingComplexityRequest,
    ReduceReadingTimeRequest,
    SummarizeIntoStepsRequest,
    SummarizeRequest,
    TranslateRequest,
    UsageQueryRequest,
)
from .responses.authoring import (
    ChainLink,
    ChangeToneData,
    ChangeToneResponse,
    ExpandWritingData,
    ExpandWritingResponse,
    FixGrammarData,
    FixGrammarResponse,
    ImproveWritingData,
    ImproveWritingResponse,
    MetadataData,
    MetadataResponse,
    ReduceReadingComplexityData,
    ReduceReadingComplexityResponse,
    ReduceReadingTimeData,
    ReduceReadingTimeResponse,
    SummarizeData,
    SummarizeIntoStepsData,
    SummarizeIntoStepsResponse,
    SummarizeResponse,
    TranslateData,
    TranslateResponse,
    UsageItem,
    UsageResponse,
)

router = APIRouter()


#################################################
# Metadata/Information
#################################################
@router.get(
    "/",
    response_model=MetadataResponse,
    status_code=status.HTTP_200_OK,
    description="Get metadata on available prompts.",
    tags=["authoring"],
)
@inject
async def get_metadata(
    assets_repo: AssetsRepositoryInterface = Depends(
        Provide[Container.assets_s3_cached_repository]
    ),
    templates_filename: str = Depends(
        Provide[Container.config.AUTHORING_PROMPTS_TEMPLATES_FILE]
    ),
) -> Any:
    """
    Get metadata on available prompts.
    """
    raw_metadata = assets_repo.get_json_asset(templates_filename)
    data = MetadataData.parse_obj(raw_metadata)

    return MetadataResponse(data=data)


@router.get(
    "/usage",
    response_model=UsageResponse,
    status_code=status.HTTP_200_OK,
    description="Get logs of usage for authoring prompts.",
    tags=["authoring", "usage"],
)
@inject
async def get_usage(
    request: UsageQueryRequest = Depends(),
    usage_log_repository: UsageLogRepository = Depends(
        Provide[Container.usage_log_repository]
    ),
) -> Any:
    usage_log_repository.filters = {
        "search": request.search,
        "org_id": request.org_id,
        "prompts": request.prompts,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "failed": request.failed,
    }

    paginated = usage_log_repository.paginated(
        page=request.page,
        per_page=request.per_page,
        sort_by=request.sort_by,
        sort_dir=request.sort_dir,
    )

    items = [
        UsageItem(
            chain_id=record["chain_id"],
            chain_operation=record["chain_operation"],
            user_id=int(record["user_id"]),
            org_id=int(record["org_id"]),
            project_id=int(record["project_id"]),
            chain_links=[ChainLink(**link) for link in record["chain_links"]],
        )
        for record in paginated["records"]
    ]

    return UsageResponse(
        meta=PaginationResponseMeta(**paginated["meta"]),
        data=items,
    )


#################################################
# Prompts
#################################################
@router.post(
    "/fix-grammar",
    response_model=FixGrammarResponse,
    status_code=status.HTTP_200_OK,
    description="Execute fix grammar prompt.",
    tags=["authoring"],
)
@inject
async def fix_grammar(
    request: FixGrammarRequest,
    fix_grammar_service: FixGrammarAuthoringService = Depends(
        Provide[Container.authoring_fix_grammar_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    """
    Execute fix grammar prompt.
    """

    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=FixGrammarAuthoringService.OPERATION_NAME,
        services=[fix_grammar_service, moderation_check_service],
    ).resolve(request.text)
    data = FixGrammarData(text=output)

    return FixGrammarResponse(data=data)


@router.post(
    "/summarize",
    response_model=SummarizeResponse,
    status_code=status.HTTP_200_OK,
    description="Summarize text.",
    tags=["authoring"],
)
@inject
async def summarize(
    request: SummarizeRequest,
    summarize_service: SummarizeService = Depends(
        Provide[Container.authoring_summarize_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    """
    Summarize text.
    """

    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=SummarizeService.OPERATION_NAME,
        services=[summarize_service, moderation_check_service],
    ).resolve(request.text)
    data = SummarizeData(text=output)

    return SummarizeResponse(data=data)


@router.post(
    "/summarize-into-steps",
    response_model=SummarizeIntoStepsResponse,
    status_code=status.HTTP_200_OK,
    description="Summarize text into steps.",
    tags=["authoring"],
)
@inject
async def summarize_into_steps(
    request: SummarizeIntoStepsRequest,
    summarize_into_steps_service: SummarizeIntoStepsService = Depends(
        Provide[Container.authoring_summarize_into_steps_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    """
    Summarize text into steps.
    """

    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=SummarizeIntoStepsService.OPERATION_NAME,
        services=[summarize_into_steps_service, moderation_check_service],
    ).resolve(request.text)
    data = SummarizeIntoStepsData(text=output)

    return SummarizeIntoStepsResponse(data=data)


@router.post(
    "/change-tone",
    response_model=ChangeToneResponse,
    status_code=status.HTTP_200_OK,
    description="Change text tone.",
    tags=["authoring"],
)
@inject
async def change_tone(
    request: ChangeToneRequest,
    change_tone_service: ChangeToneService = Depends(
        Provide[Container.authoring_change_tone_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    """
    Change text tone.
    """

    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=ChangeToneService.OPERATION_NAME,
        services=[change_tone_service, moderation_check_service],
    ).resolve(request.text, tone=request.tone)
    data = ChangeToneData(text=output)

    return ChangeToneResponse(data=data)


@router.post(
    "/translate",
    response_model=TranslateResponse,
    status_code=status.HTTP_200_OK,
    description="Translate text.",
    tags=["authoring"],
)
@inject
async def translate(
    request: TranslateRequest,
    translate_service: TranslateService = Depends(
        Provide[Container.authoring_translate_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    """
    Translate text.
    """

    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=TranslateService.OPERATION_NAME,
        services=[moderation_check_service, translate_service],
    ).resolve(request.text, language=request.language)
    data = TranslateData(text=output)

    return TranslateResponse(data=data)


@router.post(
    "/improve-writing",
    response_model=ImproveWritingResponse,
    status_code=status.HTTP_200_OK,
    description="Improve writing.",
    tags=["authoring"],
)
@inject
async def improve_writing(
    request: ImproveWritingRequest,
    improve_writing_service: ImproveWritingService = Depends(
        Provide[Container.authoring_improve_writing_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    """
    Improve writing.
    """

    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=ImproveWritingService.OPERATION_NAME,
        services=[improve_writing_service, moderation_check_service],
    ).resolve(request.text)
    data = ImproveWritingData(text=output)

    return ImproveWritingResponse(data=data)


@router.post(
    "/reduce-reading-complexity",
    response_model=ReduceReadingComplexityResponse,
    status_code=status.HTTP_200_OK,
    description="Reduce reading complexity.",
    tags=["authoring"],
)
@inject
async def reduce_reading_complexity(
    request: ReduceReadingComplexityRequest,
    reduce_reading_complexity_service: ReduceReadingComplexityService = Depends(  # noqa
        Provide[Container.reduce_reading_complexity_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=ReduceReadingComplexityService.OPERATION_NAME,
        services=[reduce_reading_complexity_service, moderation_check_service],
    ).resolve(request.text)
    data = ReduceReadingComplexityData(text=output)

    return ReduceReadingComplexityResponse(data=data)


@router.post(
    "/reduce-reading-time",
    response_model=ReduceReadingTimeResponse,
    status_code=status.HTTP_200_OK,
    description="Reduce reading time.",
    tags=["authoring"],
)
@inject
async def reduce_reading_time(
    request: ReduceReadingTimeRequest,
    reduce_reading_time_service: ReduceReadingTimeService = Depends(  # noqa
        Provide[Container.reduce_reading_time_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=ReduceReadingTimeService.OPERATION_NAME,
        services=[reduce_reading_time_service, moderation_check_service],
    ).resolve(request.text)
    data = ReduceReadingTimeData(text=output)

    return ReduceReadingTimeResponse(data=data)


@router.post(
    "/expand-writing",
    response_model=ExpandWritingResponse,
    status_code=status.HTTP_200_OK,
    description="Expand writing.",
    tags=["authoring"],
)
@inject
async def expand_writing(
    request: ExpandWritingRequest,
    expand_writing_service: ExpandWritingService = Depends(  # noqa
        Provide[Container.expand_writing_service]
    ),
    moderation_check_service: ModerationCheckOrFailService = Depends(
        Provide[Container.moderation_check_service]
    ),
    audit_repository: AuditInMemoryRepository = Depends(
        Provide[Container.audit_repository]
    ),
) -> Any:
    audit_repository.set_from_metadata(request.metadata.dict())

    output = ChainResolver(
        operation=ExpandWritingService.OPERATION_NAME,
        services=[expand_writing_service, moderation_check_service],
    ).resolve(request.text)
    data = ExpandWritingData(text=output)

    return ExpandWritingResponse(data=data)
