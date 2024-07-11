from dependency_injector import containers, providers

import src.repositories.models.analytics.semantic_search_analytics_repository as ssar  # noqa: E501
from src.core.deps.chunker import get_chunker
from src.repositories.assets import S3CachedAssetsRepository
from src.repositories.audit import AuditInMemoryRepository
from src.repositories.models.usage_log_repository import UsageLogRepository
from src.repositories.services.config_svc import ConfigSvcRepository
from src.repositories.services.connectors_svc import ConnectorsSvcRepository
from src.repositories.services.lime import LimeRepository
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
from src.services.data.transformations.article_kb import (
    BronzeToSilverService as SalesforceKBBronzeToSilverService,
)
from src.services.data.transformations.article_kb import (
    SilverToGoldService as SalesforceKBSilverToGoldService,
)
from src.services.data.transformations.html import (
    SilverToGoldService as HtmlSilverToGoldService,
)
from src.services.data.transformations.zt_trees import (
    BronzeToSilverService as ZTBronzeToSilverService,
)
from src.services.data.transformations.zt_trees import (
    RawToBronzeService as ZTRawToBronzeService,
)
from src.services.data.transformations.zt_trees import (
    SilverToGoldService as ZTSilverToGoldService,
)
from src.services.moderation import (
    ModerationCheckOrFailService,
    ModerationService,
)
from src.util.cache import RedisCache
from src.util.storage import S3Storage

from ..repositories.models.semantic_search_repository import (
    SemanticSearchRepository,
)
from ..services.semantic_search import (
    SemanticSearchService,
    SummarizeAnswerService,
)
from .config import get_settings
from .deps.ai_client import get_open_ai_client
from .deps.boto3 import get_client, get_session
from .deps.database import Database, MysqlDatabase
from .deps.embedder import get_embedder
from .deps.kafka import get_consumer, get_producer
from .deps.redis import get_redis_client
from .deps.slack import get_slack_service
from .deps.summarizer import get_summarizer


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # DB
    db = providers.Singleton(Database, config=config)
    mysql_db = providers.Singleton(MysqlDatabase, config=config)

    # Kafka
    kafka_producer = providers.Singleton(
        get_producer,
        configs={
            "bootstrap.servers": get_settings().KAFKA_BOOTSTRAP_SERVERS,
            "security.protocol": get_settings().KAFKA_SECURITY_PROTOCOL,
        },
    )

    kafka_consumer = providers.Singleton(
        get_consumer,
        configs={
            "bootstrap.servers": get_settings().KAFKA_BOOTSTRAP_SERVERS,
            "group.id": get_settings().KAFKA_GROUP_ID,
            "auto.offset.reset": "earliest",
            "security.protocol": get_settings().KAFKA_SECURITY_PROTOCOL,
        },
    )

    # Cache
    redis_pool = providers.Resource(
        get_redis_client,
        url=config.REDIS_URL,
        db=config.REDIS_CACHE_DB,
    )

    cache_redis = providers.Factory(RedisCache, client=redis_pool)

    # Storage
    boto3_session = providers.Resource(
        get_session,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_DEFAULT_REGION,
    )

    s3_client = providers.Resource(
        get_client, session=boto3_session.provided, service_name="s3"
    )

    storage_s3 = providers.Factory(S3Storage, client=s3_client)

    # Repositories
    audit_repository = providers.Singleton(AuditInMemoryRepository)

    assets_s3_cached_repository = providers.Factory(
        S3CachedAssetsRepository,
        cache=cache_redis,
        storage=storage_s3,
        bucket=config.ASSETS_S3_BUCKET,
        ttl=config.ASSETS_CACHE_TTL,
    )

    usage_log_repository = providers.Factory(
        UsageLogRepository,
        session_factory=db.provided.session,
        audit_repository=audit_repository,
    )

    semantic_search_repository = providers.Factory(
        SemanticSearchRepository,
        session_factory=db.provided.session,
    )

    # Analytics Repositories
    semantic_search_analytics_repository = providers.Factory(
        ssar.SemanticSearchAnalyticsRepository,
        session_factory=mysql_db.provided.session,
        audit_repository=audit_repository,
    )

    # Services
    connectors_svc_repository = providers.Factory(
        ConnectorsSvcRepository,
        url=config.CONNECTORS_SVC_URL,
    )

    config_svc_repository = providers.Factory(
        ConfigSvcRepository,
        url=config.CONFIG_SVC_URL,
    )

    lime_repository = providers.Factory(
        LimeRepository,
        url=config.LIME_URL,
        key=config.SERVICE_TO_SERVICE_KEY,
    )

    # AI API Client
    open_ai_api_client = providers.Factory(
        get_open_ai_client,
        org_id=config.OPENAI_ORG_ID,
        api_key=config.OPENAI_API_KEY,
        usage_log_repository=usage_log_repository,
    )

    # Slack Client
    slack_service = providers.Factory(
        get_slack_service,
        channel_id=config.SLACK_CHANNEL_ID,
        token=config.SLACK_TOKEN,
    )

    # Services
    authoring_fix_grammar_service = providers.Factory(
        FixGrammarAuthoringService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    authoring_summarize_service = providers.Factory(
        SummarizeService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    authoring_summarize_into_steps_service = providers.Factory(
        SummarizeIntoStepsService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    authoring_change_tone_service = providers.Factory(
        ChangeToneService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    authoring_translate_service = providers.Factory(
        TranslateService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    authoring_improve_writing_service = providers.Factory(
        ImproveWritingService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    reduce_reading_complexity_service = providers.Factory(
        ReduceReadingComplexityService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    reduce_reading_time_service = providers.Factory(
        ReduceReadingTimeService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    expand_writing_service = providers.Factory(
        ExpandWritingService,
        ai_api_client=open_ai_api_client,
        assets_repo=assets_s3_cached_repository,
        templates_filename=config.AUTHORING_PROMPTS_TEMPLATES_FILE,
        slack_service=slack_service,
    )

    # Moderation
    moderation_service = providers.Factory(
        ModerationService,
        ai_api_client=open_ai_api_client,
    )

    moderation_check_service = providers.Factory(
        ModerationCheckOrFailService,
        moderation_service=moderation_service,
    )

    # Semantic Search
    chunker = providers.Factory(
        get_chunker,
        chunking_method=config.SEMANTIC_SEARCH_CHUNKING_METHOD,
        snippet_length=config.SEMANTIC_SEARCH_CHUNK_LENGTH,
        concat_type=config.SEMANTIC_SEARCH_CONCAT,
    )

    embedder = providers.Factory(
        get_embedder,
        endpoint_type=config.EMBEDDINGS_ENDPOINT_TYPE,
        endpoint_name=config.EMBEDDINGS_ENDPOINT_NAME,
        aws_region=config.AWS_DEFAULT_REGION,
    )

    summarizer = providers.Factory(
        get_summarizer,
        assets_repo=assets_s3_cached_repository,
        endpoint_type=config.SUMMARIZER_ENDPOINT_TYPE,
        endpoint_name=config.SUMMARIZER_ENDPOINT_NAME,
        aws_region=config.AWS_DEFAULT_REGION,
        prompt_type=config.SUMMARIZER_PROMPT_TYPE,
        config_filename=config.SUMMARIZER_CONFIG_FILE,
    )

    semantic_search_service = providers.Factory(
        SemanticSearchService,
        embedder=embedder,
        items_repository=semantic_search_repository,
        semantic_search_analytics_repository=semantic_search_analytics_repository,  # noqa: E501
        connectors_svc_repository=connectors_svc_repository,
        config_svc_repository=config_svc_repository,
        lime_repository=lime_repository,
        audit_repository=audit_repository,
    )

    summarize_answer_service = providers.Factory(
        SummarizeAnswerService,
        embedder=embedder,
        summarizer=summarizer,
        items_repository=semantic_search_repository,
        app_env=config.APP_ENV,
        connectors_svc_repository=connectors_svc_repository,
        config_svc_repository=config_svc_repository,
    )

    # Data
    # Transformations
    # ZT Trees
    zt_trees_raw_to_bronze_service = providers.Factory(
        ZTRawToBronzeService,
        assets_repo=storage_s3,
        event_producer=kafka_producer,
    )

    zt_trees_bronze_to_silver_service = providers.Factory(
        ZTBronzeToSilverService,
        assets_repo=storage_s3,
        event_producer=kafka_producer,
    )

    zt_trees_silver_to_gold_service = providers.Factory(
        ZTSilverToGoldService,
        assets_repo=storage_s3,
        event_producer=kafka_producer,
        embedder=embedder,
        items_repository=semantic_search_repository,
        chunker=chunker,
        connectors_service=connectors_svc_repository,
    )

    # HTML
    html_silver_to_gold_service = providers.Factory(
        HtmlSilverToGoldService,
        assets_repo=storage_s3,
        embedder=embedder,
        items_repository=semantic_search_repository,
        chunker=chunker,
        connectors_service=connectors_svc_repository,
    )

    # Article KB
    article_kb_bronze_to_silver_service = providers.Factory(
        SalesforceKBBronzeToSilverService,
        assets_repo=storage_s3,
        event_producer=kafka_producer,
        app_url=config.APP_URL,
        silver_to_gold_enable=config.SILVER_TO_GOLD_ENABLE,
    )

    article_kb_silver_to_gold_service = providers.Factory(
        SalesforceKBSilverToGoldService,
        assets_repo=storage_s3,
        event_producer=kafka_producer,
        embedder=embedder,
        items_repository=semantic_search_repository,
        chunker=chunker,
    )


# Start the container
container = Container()
container.config.from_pydantic(get_settings())
