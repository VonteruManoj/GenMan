import os
from unittest.mock import ANY, Mock

import pytest

from src.api.v1.endpoints.requests.semantic_search import SearchFilters
from src.api.v1.endpoints.responses.semantic_search import TagMeta
from src.core.containers import container
from src.schemas.services.config_svc import SearchWidget
from src.schemas.services.connectors_svc import Connector, ConnectorType
from src.services.semantic_search import (
    SemanticSearchService,
    SummarizeAnswerService,
)
from src.util.tags_parser import TagParser
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


def create_widget_valid_items():
    config_svc_mock = Mock()
    config_svc_mock.get_search_widget_by_deployment_id.return_value = (
        SearchWidget.parse_obj(
            {
                "id": 1,
                "name": "widget",
                "type": "agent",
                "deploymentId": "9a44ad83-a9d2-427d-a8c9-91040d2b6e84",
                "deployStandalone": True,
                "deployInTree": True,
                "deployEmbedded": True,
                "deploySalesforce": True,
                "enableDecisionTrees": True,
                "enableExternalSources": True,
                "orgId": 1,
                "active": True,
                "createdAt": "2023-11-13T12:28:21Z",
                "updatedAt": "2023-11-13T12:38:54Z",
                "metadataInfo": {
                    "sourcesConfig": {
                        "decisionTree": {
                            "all": True,
                            "treeIds": [1, 2],
                            "displayTags": True,
                            "listTreesOnStartup": False,
                            "treeLabel": "Scripts",
                        },
                        "externalSource": {"connectorIds": [1, 2]},
                    },
                    "deployment": {
                        "standalone": {
                            "url": "https://zingtree.com/alpha-search",
                            "pageTitle": "My Search",
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            },
                        },
                        "inTree": {
                            "all": True,
                            "treeIds": [1, 2],
                            "placement": "top",
                            "authMode": "authenticated-user",
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            },
                        },
                        "embedded": {
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            }
                        },
                        "salesforce": {
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            }
                        },
                    },
                },
            }
        )
    )

    connectors_svc_mock = Mock()
    ctzt = ConnectorType(
        id=1, name="test", description="test", provider="zingtree", active=True
    )
    ctsfk = ConnectorType(
        id=1,
        name="test",
        description="test",
        provider="salesforce",
        active=True,
    )
    c1 = Connector(
        id=1, name="test", description="test", active=True, connector_type=ctzt
    )
    c2 = Connector(
        id=2,
        name="test",
        description="test",
        active=True,
        connector_type=ctsfk,
    )

    connectors_svc_mock.get_all_connectors.return_value = [c1, c2]

    return config_svc_mock, connectors_svc_mock


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search():
    embed_mock = Mock()
    embed_mock.embed.return_value = [[0.1] * embeddings_dimensions]
    repository = container.semantic_search_repository()
    analytics_repository = container.semantic_search_analytics_repository()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=1
    )

    config_svc_mock, connectors_svc_mock = create_widget_valid_items()

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )
    filters = SearchFilters()
    results = semantic_search_service.search(
        search="test",
        org_id=1,
        deployment_id="test-uuid",
        filters=filters,
        limit=5,
    )

    assert len(results[0]["options"]) == 2
    embed_mock.embed.assert_called_once_with("test")
    # No errors
    assert results[1] is False

    connectors_svc_mock.get_all_connectors.assert_called_once_with(1)
    config_svc_mock.get_search_widget_by_deployment_id.assert_called_once_with(
        1, "test-uuid"
    )


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search_creates_analytics_batch():
    embed_mock = Mock()
    embed_mock.embed.return_value = [[0.1] * embeddings_dimensions]
    repository = container.semantic_search_repository()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    # create analytics batch
    batch = container.semantic_search_analytics_repository().create_batch(
        operation="search", deployment_id="test-uuid"
    )

    # Mock analytics repository
    analytics_repository = Mock()
    analytics_repository.from_search.return_value = batch

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=1
    )

    config_svc_mock, connectors_svc_mock = create_widget_valid_items()

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )
    filters = SearchFilters(connectors=[1, 2])
    results = semantic_search_service.search(
        search="test",
        org_id=1,
        deployment_id="test-uuid",
        filters=filters,
        limit=5,
    )
    assert "analytics_id" in results[0]
    assert results[0]["analytics_id"] == str(batch.id)

    # anlytic sfrom search is been called
    filters.zt_connector_id = 1
    filters.zt_tree_ids = None
    analytics_repository.from_search.assert_called_once()
    analytics_repository.from_search.assert_called_once_with(
        search="test",
        limit=5,
        sort_by="relevance",
        options=ANY,
        distances=ANY,
        filters=filters.dict(),
        deployment_id="test-uuid",
    )

    connectors_svc_mock.get_all_connectors.assert_called_once_with(1)
    config_svc_mock.get_search_widget_by_deployment_id.assert_called_once_with(
        1, "test-uuid"
    )


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search_no_items():
    embed_mock = Mock()
    embed_mock.embed.return_value = [[0.1] * embeddings_dimensions]
    repository = container.semantic_search_repository()
    analytics_repository = container.semantic_search_analytics_repository()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, connector_id=1
    )

    config_svc_mock, connectors_svc_mock = create_widget_valid_items()

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )
    filters = SearchFilters()
    results = semantic_search_service.search(
        search="test",
        org_id=2,
        deployment_id="test-uuid",
        filters=filters,
        limit=5,
    )

    assert len(results[0]["options"]) == 0
    embed_mock.embed.assert_called_once_with("test")
    # No errors
    assert results[1] is False
    assert "analytics_id" in results[0]
    assert results[0] is not None

    connectors_svc_mock.get_all_connectors.assert_called_once_with(2)
    config_svc_mock.get_search_widget_by_deployment_id.assert_called_once_with(
        2, "test-uuid"
    )


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search_partial_response(check_log_message):
    embed_mock = Mock()
    embed_mock.embed.return_value = [[0.1] * embeddings_dimensions]
    repository = container.semantic_search_repository()
    analytics_repository = container.semantic_search_analytics_repository()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, tags="oops!", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=1
    )

    config_svc_mock, connectors_svc_mock = create_widget_valid_items()

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )
    filters = SearchFilters()
    results = semantic_search_service.search(
        search="test",
        org_id=1,
        deployment_id="test-uuid",
        filters=filters,
        limit=5,
    )

    assert len(results[0]["options"]) == 1
    embed_mock.embed.assert_called_once_with("test")
    # With errors
    assert results[1] is True
    check_log_message(
        "ERROR",
        "[Semantic-Search] Failed to map option to dict",
    )

    connectors_svc_mock.get_all_connectors.assert_called_once_with(1)
    config_svc_mock.get_search_widget_by_deployment_id.assert_called_once_with(
        1, "test-uuid"
    )


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search_only_returns_best_chunk_per_document():
    embed_mock = Mock()
    embed_mock.embed.return_value = [[0.1] * embeddings_dimensions]
    repository = container.semantic_search_repository()
    analytics_repository = container.semantic_search_analytics_repository()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    # Create 2 items with the same document id
    d1 = SemanticSearchDocumentFactory(
        org_id=1,
        items__embeddings=[0.05] * embeddings_dimensions,
        items=2,
        connector_id=1,
    )
    d2 = SemanticSearchDocumentFactory(
        org_id=1,
        items__embeddings=[0.5] * embeddings_dimensions,
        items=2,
        connector_id=1,
    )

    config_svc_mock, connectors_svc_mock = create_widget_valid_items()

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )
    filters = SearchFilters()
    results = semantic_search_service.search(
        search="test",
        org_id=1,
        deployment_id="test-uuid",
        filters=filters,
        limit=5,
    )

    assert len(results[0]) == 2
    embed_mock.embed.assert_called_once_with("test")
    # Order
    assert results[0]["options"][0]["document"]["id"] == d1.id
    assert results[0]["options"][1]["document"]["id"] == d2.id
    # No errors
    assert results[1] is False

    connectors_svc_mock.get_all_connectors.assert_called_once_with(1)
    config_svc_mock.get_search_widget_by_deployment_id.assert_called_once_with(
        1, "test-uuid"
    )


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search_returns_distance_at_result_level():
    embed_mock = Mock()
    embed_mock.embed.return_value = [[0.1] * embeddings_dimensions]
    repository = container.semantic_search_repository()
    analytics_repository = container.semantic_search_analytics_repository()
    SemanticSearchDocumentFactory(org_id=1, items=2, connector_id=1)
    SemanticSearchDocumentFactory(org_id=1, items=2, connector_id=2)
    config_svc_mock, connectors_svc_mock = create_widget_valid_items()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )
    filters = SearchFilters()
    results = semantic_search_service.search(
        search="test",
        org_id=1,
        deployment_id="test-uuid",
        filters=filters,
        limit=5,
    )

    assert len(results[0]) == 2
    embed_mock.embed.assert_called_once_with("test")
    # Order
    assert results[0]["options"][0]["distance"] is not None
    assert isinstance(results[0]["options"][0]["distance"], float)
    assert results[0]["options"][1]["distance"] is not None
    assert isinstance(results[0]["options"][1]["distance"], float)
    # No errors
    assert results[1] is False

    connectors_svc_mock.get_all_connectors.assert_called_once_with(1)
    config_svc_mock.get_search_widget_by_deployment_id.assert_called_once_with(
        1, "test-uuid"
    )


def test_get_tags():
    repository_mock = Mock()
    tags = {
        "tag-1": ["v1", "v2"],
        "tag-2": ["v2", "v3"],
    }
    repository_mock.get_tags.return_value = TagParser(tags).to_str()
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    semantic_search_service = SemanticSearchService(
        Mock(), repository_mock, Mock(), Mock(), Mock(), Mock(), audit_mock
    )

    got, meta = semantic_search_service.get_tags(1)

    assert tags == got
    assert meta is None

    repository_mock.get_tags.assert_called_once_with(1)


def test_get_tags_with_connectors_count():
    repository_mock = Mock()
    repository_mock.get_tags_with_meta.return_value = {
        ('"tag-1"."v1"', 1, 22),
        ('"tag-1"."v2"', 2, 2),
        ('"tag-2"."v2"', 3, 3),
        ('"tag-2"."v3"', 4, 44),
    }
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    semantic_search_service = SemanticSearchService(
        Mock(), repository_mock, Mock(), Mock(), Mock(), Mock(), audit_mock
    )

    got, meta = semantic_search_service.get_tags(1, ["connectorsCount"])

    assert "tag-1" in got
    assert "v1" in got["tag-1"]
    assert "v2" in got["tag-1"]
    assert "tag-2" in got
    assert "v2" in got["tag-2"]
    assert "v3" in got["tag-2"]

    assert "connectorsCount" in meta
    assert (
        TagMeta(tag="tag-1", value="v1", connectorId=1, count=22)
        in meta["connectorsCount"]
    )
    assert (
        TagMeta(tag="tag-1", value="v2", connectorId=2, count=2)
        in meta["connectorsCount"]
    )
    assert (
        TagMeta(tag="tag-2", value="v2", connectorId=3, count=3)
        in meta["connectorsCount"]
    )
    assert (
        TagMeta(tag="tag-2", value="v3", connectorId=4, count=44)
        in meta["connectorsCount"]
    )

    repository_mock.get_tags_with_meta.assert_called_once_with(1)


def test_get_connectors():
    repository_mock = Mock()
    repository_mock.get_all_connectors.return_value = []
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False

    semantic_search_service = SemanticSearchService(
        Mock(), Mock(), Mock(), repository_mock, Mock(), Mock(), audit_mock
    )

    cs = semantic_search_service.get_connectors(1)

    assert len(cs) == 0
    repository_mock.get_all_connectors.assert_called_once_with(org_id=1)


def setup_summarize_mocks():
    mock_embedder = Mock()
    mock_summarizer = Mock()
    mock_items_repository = Mock()
    config_svc_mock, connectors_svc_mock = create_widget_valid_items()
    summarize_answer_service = SummarizeAnswerService(
        mock_embedder,
        mock_summarizer,
        mock_items_repository,
        "",
        connectors_svc_mock,
        config_svc_mock,
    )
    return (
        mock_embedder,
        mock_summarizer,
        mock_items_repository,
        summarize_answer_service,
    )


def test_handle_with_options_id_list_returns_summarized_answer():
    (
        _,
        mock_summarizer,
        mock_items_repository,
        summarize_answer_service,
    ) = setup_summarize_mocks()
    item1 = Mock(text="text1")
    item1.to_dict.return_value = {"text": "text1"}
    item2 = Mock(text="text2")
    item2.to_dict.return_value = {"text": "text2"}
    mock_items_repository.find_semantic_search_items_by_ids.return_value = [
        item1,
        item2,
    ]
    mock_summarizer.summarize.return_value = "summarized_answer"
    result = summarize_answer_service.handle("query", 1, "deploy-uuid", [1, 2])
    assert result["answer"] == "summarized_answer"
    assert len(result["options"]) == 2
    assert result["options"][0]["text"] == "text1"
    assert result["options"][1]["text"] == "text2"


def test_handle_without_options_id_list_returns_summarized_answer():
    (
        mock_embedder,
        mock_summarizer,
        mock_items_repository,
        summarize_answer_service,
    ) = setup_summarize_mocks()
    mock_embedder.embed.return_value = ["embeddings1", "embeddings2"]
    item1 = Mock(text="text1")
    item1.to_dict.return_value = {"text": "text1"}
    item2 = Mock(text="text2")
    item2.to_dict.return_value = {"text": "text2"}
    mock_items_repository.search_best.return_value = [
        item1,
        item2,
    ]
    mock_summarizer.summarize.return_value = "summarized_answer"
    result = summarize_answer_service.handle("query", 1, "deploy-uuid")
    assert result["answer"] == "summarized_answer"
    assert len(result["options"]) == 2
    assert result["options"][0]["text"] == "text1"
    assert result["options"][1]["text"] == "text2"


def test_handle_with_empty_options_returns_error_message():
    (
        mock_embedder,
        _,
        mock_items_repository,
        summarize_answer_service,
    ) = setup_summarize_mocks()
    mock_embedder.embed.return_value = ["embeddings1", "embeddings2"]
    mock_items_repository.search_best.return_value = []
    result = summarize_answer_service.handle("query", 1, "deploy-uuid")
    assert result["answer"] == "There is no context to answer this question."
    assert len(result["options"]) == 0


def test_get_documents():
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False
    repository_mock = Mock()

    repository_mock.get_documents.return_value = (
        SemanticSearchDocumentFactory.create_batch(2, org_id=1, items=2)
    )

    semantic_search_service = SemanticSearchService(
        Mock(), repository_mock, Mock(), Mock(), Mock(), Mock(), audit_mock
    )

    got = semantic_search_service.get_documents(
        org_id=1,
        connector_id=2,
        limit=10,
        offset=0,
    )

    assert len(got) == 2
    repository_mock.get_documents.assert_called_once_with(
        org_id=1,
        connector_id=2,
        limit=10,
        offset=0,
    )


def test_get_languages():
    audit_mock = Mock()
    audit_mock.is_agent.return_value = False
    repository_mock = Mock()

    repository_mock.get_languages.return_value = ["en", "es"]

    semantic_search_service = SemanticSearchService(
        Mock(), repository_mock, Mock(), Mock(), Mock(), Mock(), audit_mock
    )

    got = semantic_search_service.get_languages(
        org_id=1,
    )

    assert len(got) == 2
    repository_mock.get_languages.assert_called_once_with(
        org_id=1,
    )


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_semantic_search_deployment_has_document():
    embed_mock = Mock()
    repository = container.semantic_search_repository()
    analytics_repository = container.semantic_search_analytics_repository()
    audit_mock = Mock()
    SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=1
    )

    config_svc_mock, connectors_svc_mock = create_widget_valid_items()

    semantic_search_service = SemanticSearchService(
        embed_mock,
        repository,
        analytics_repository,
        connectors_svc_mock,
        config_svc_mock,
        Mock(),
        audit_mock,
    )

    audit_mock.data.org_id = 1
    result = semantic_search_service.deployment_has_documents(
        deployment_id="test-uuid",
    )
    assert result is True
    audit_mock.data.org_id = 2
    result = semantic_search_service.deployment_has_documents(
        deployment_id="test-uuid",
    )
    assert result is True
    audit_mock.data.org_id = 3
    result = semantic_search_service.deployment_has_documents(
        deployment_id="test-uuid",
    )
    assert result is False
