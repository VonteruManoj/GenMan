from unittest.mock import Mock, patch

import src.repositories.models.analytics.semantic_search_analytics_repository as ssra  # noqa: E501
from src.contracts.adapters.ai_api import AIApiClientInterface
from src.contracts.embedder import EmbedderInterface
from src.contracts.summarizer import SummarizerInterface
from src.core.config import get_settings
from src.core.containers import Container
from src.data.chunkers.chunker import Chunker
from src.repositories.assets import S3CachedAssetsRepository
from src.repositories.models.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.repositories.models.usage_log_repository import UsageLogRepository
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
from src.services.semantic_search import (
    SemanticSearchService,
    SummarizeAnswerService,
)
from src.services.slack import FakeSlackService
from src.util.cache import RedisCache
from src.util.storage import S3Storage


# ----------------------------------------------
# Factories
# ----------------------------------------------
def test_slack_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.slack_service(), FakeSlackService)


def test_moderation_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.moderation_service(), ModerationService)


def test_moderation_check_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.moderation_check_service(), ModerationCheckOrFailService
    )


def test_cache_redis_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.cache_redis(), RedisCache)


def test_storage_s3_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.storage_s3(), S3Storage)


def test_assets_s3_cached_repository_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.assets_s3_cached_repository(), S3CachedAssetsRepository
    )


def test_usage_log_repository_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.usage_log_repository(), UsageLogRepository)


def test_semantic_search_repository_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.semantic_search_repository(), SemanticSearchRepository
    )


def test_semantic_search_analytics_repository_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.semantic_search_analytics_repository(),
        ssra.SemanticSearchAnalyticsRepository,
    )


def test_open_ai_client_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.open_ai_api_client(), AIApiClientInterface)


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_authoring_fix_grammar_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.authoring_fix_grammar_service(), FixGrammarAuthoringService
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_authoring_summarize_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.authoring_summarize_service(), SummarizeService
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_authoring_summarize_into_steps_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.authoring_summarize_into_steps_service(),
        SummarizeIntoStepsService,
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_authoring_change_tone_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.authoring_change_tone_service(), ChangeToneService
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_authoring_translate_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.authoring_translate_service(), TranslateService
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_authoring_improve_writing_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.authoring_improve_writing_service(), ImproveWritingService
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_reduce_reading_complexity_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.reduce_reading_complexity_service(),
        ReduceReadingComplexityService,
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_reduce_reading_time_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.reduce_reading_time_service(),
        ReduceReadingTimeService,
    )


@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
def test_expand_writing_service_factory(
    mock_get_json_asset, make_prompt_templates_plain
):
    mock_get_json_asset.return_value = make_prompt_templates_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.expand_writing_service(),
        ExpandWritingService,
    )


def test_chunker_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.chunker(), Chunker)


def test_embedder_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.embedder(), EmbedderInterface)


@patch("src.core.containers.S3Storage.get_json")
def test_summarizer_factory(get_json_mock, make_summarizer_config_plain):
    get_json_mock.return_value = make_summarizer_config_plain()

    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(container.summarizer(), SummarizerInterface)


def test_semantic_search_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    with container.embedder.override(Mock()):
        assert isinstance(
            container.semantic_search_service(), SemanticSearchService
        )


def test_summarize_answer_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    with container.summarizer.override(Mock()):
        assert isinstance(
            container.summarize_answer_service(), SummarizeAnswerService
        )


def test_zt_trees_raw_to_bronze_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.zt_trees_raw_to_bronze_service(),
        ZTRawToBronzeService,
    )


def test_zt_trees_bronze_to_silver_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.zt_trees_bronze_to_silver_service(),
        ZTBronzeToSilverService,
    )


def test_zt_trees_silver_to_gold_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.zt_trees_silver_to_gold_service(),
        ZTSilverToGoldService,
    )


def test_html_silver_to_gold_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.html_silver_to_gold_service(),
        HtmlSilverToGoldService,
    )


def test_article_kb_bronze_to_silver_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.article_kb_bronze_to_silver_service(),
        SalesforceKBBronzeToSilverService,
    )


def test_article_kb_silver_to_gold_service_factory():
    container = Container()
    container.config.from_pydantic(get_settings())

    assert isinstance(
        container.article_kb_silver_to_gold_service(),
        SalesforceKBSilverToGoldService,
    )
