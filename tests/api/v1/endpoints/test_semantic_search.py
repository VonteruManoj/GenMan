import json
import os
from unittest.mock import call, patch

import pytest
from fastapi.testclient import TestClient

from src.core.containers import container
from src.main import app
from src.models.analytics.semantic_search import (
    SemanticSearchAnalytic,
    SemanticSearchAnalyticEvent,
)
from src.models.semantic_search_item import SemanticSearchItem
from src.schemas.services.config_svc import SearchWidget
from src.schemas.services.connectors_svc import Connector, ConnectorType
from src.util.tags_parser import TagParser
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)

client = TestClient(app)

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


def widget_mock_data():
    widget = SearchWidget.parse_obj(
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

    return widget, c1, c2


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
def test_search(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&sortBy=relevance&filters={}"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 8

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 2
    assert response.json()["error"] is False
    assert not response.json()["error_code"]
    assert not response.json()["message"]

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
def test_search_is_filtered_by_connectors(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory(org_id=1, connector_id=1, items=2)
    SemanticSearchDocumentFactory(org_id=1, connector_id=2, items=2)
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    filters = {"connectors": [1]}
    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&sortBy=relevance"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84&filters="
        + json.dumps(filters),
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 1
    assert (
        response.json()["data"]["options"][0]["document"]["connectorId"] == 1
    )

    filters = {"connectors": [1, 2]}
    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=relevance&filters=" + json.dumps(filters),
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 2
    c1 = response.json()["data"]["options"][0]["document"]["connectorId"]
    c2 = response.json()["data"]["options"][1]["document"]["connectorId"]
    assert (c1 == 1 and c2 == 2) or (c1 == 2 and c2 == 1)

    get_all_connectors_mock.has_calls(
        call(1),
        call(1),
    )

    get_search_widget_by_deployment_id_mock.has_calls(
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
def test_search_is_filtered_by_tags(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    tags = TagParser({"tag-1": ["t1", "t2"]}).to_str()
    d1 = SemanticSearchDocumentFactory(
        org_id=1, tags=tags, items=2, connector_id=1
    )
    tags = TagParser({"tag-1": ["t2"], "tag-2": ["a"]}).to_str()
    d2 = SemanticSearchDocumentFactory(
        org_id=1, tags=tags, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    filters = json.dumps({"tags": {"tag-1": ["t1"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/search?search=hola"
        "&limit=5&orgId=1&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&sortBy=relevance&filters={filters}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 1
    assert response.json()["data"]["options"][0]["document"]["id"] == d1.id

    filters = json.dumps({"tags": {"tag-1": ["t2"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/search?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&sortBy=relevance&filters={filters}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 2
    ids = [
        response.json()["data"]["options"][0]["document"]["id"],
        response.json()["data"]["options"][1]["document"]["id"],
    ]
    assert d1.id in ids
    assert d2.id in ids

    filters = json.dumps({"tags": {"tag-1": ["t1", "t2"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/search?search=hola"
        "&limit=5&orgId=1&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&sortBy=relevance&filters={filters}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 2
    ids = [
        response.json()["data"]["options"][0]["document"]["id"],
        response.json()["data"]["options"][1]["document"]["id"],
    ]
    assert d1.id in ids
    assert d2.id in ids

    filters = json.dumps({"tags": {"tag-1": ["t1"], "tag-2": ["a"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/search?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&sortBy=relevance&filters={filters}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 2
    ids = [
        response.json()["data"]["options"][0]["document"]["id"],
        response.json()["data"]["options"][1]["document"]["id"],
    ]
    assert d1.id in ids
    assert d2.id in ids

    get_all_connectors_mock.has_calls(
        call(1),
        call(1),
        call(1),
        call(1),
    )

    get_search_widget_by_deployment_id_mock.has_calls(
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.repositories.services.lime." "LimeRepository.get_agent_tags")
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
def test_search_creates_analytics_with_one_event(
    connected_mock,
    embed_mock,
    get_agent_tags_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]
    get_agent_tags_mock.return_value = ["tag-1", "tag-2"]

    SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=1, tags=['"zt_trees_trees"."tag-1"']
    )
    SemanticSearchDocumentFactory.create_batch(
        1, org_id=2, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=relevance&filters={}",
        headers={
            "zt-causer-id": "2",
            "zt-causer-type": "App\\Models\\Agent",
            "zt-org-id": "123",
        },
    )

    with container.mysql_db().session() as session:
        assert session.query(SemanticSearchAnalytic).count() == 1
        assert session.query(SemanticSearchAnalyticEvent).count() == 1

        # get batch
        batch = session.query(SemanticSearchAnalytic).first()

    assert batch.org_id == 123
    assert batch.causer_id == 2
    assert batch.causer_type == "App\\Models\\Agent"
    assert len(batch.events) == 1
    assert batch.events[0].data["request"]["query"] == "test"
    assert len(batch.events[0].data["options"]) == 1

    # Batch id should be returned in response
    assert "analyticsId" in response.json()["data"]
    assert response.json()["data"]["analyticsId"] == str(batch.id)

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.repositories.services.lime." "LimeRepository.get_agent_tags")
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
def test_search_uses_agent_tags(
    connected_mock,
    embed_mock,
    get_agent_tags_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]
    get_agent_tags_mock.return_value = ["tag-1", "tag-2"]
    expected_ids = []
    not_expected_ids = []

    d = SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=1, tags=['"zt_trees_trees"."tag-1"']
    )
    expected_ids.append(d[0].id)
    d = SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=1, tags=['"zt_trees_trees"."tag-2"']
    )
    expected_ids.append(d[0].id)
    d = SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=2
    )
    expected_ids.append(d[0].id)
    d = SemanticSearchDocumentFactory.create_batch(
        1, org_id=1, items=2, connector_id=1, tags=['"zt_trees_trees"."tag-3"']
    )
    not_expected_ids.append(d[0].id)
    d = SemanticSearchDocumentFactory.create_batch(
        1, org_id=2, items=2, connector_id=3
    )
    not_expected_ids.append(d[0].id)
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=relevance&filters={}",
        headers={
            "zt-causer-id": "2",
            "zt-causer-type": "App\\Models\\Agent",
            "zt-org-id": "123",
        },
    )

    ids = [o["document"]["id"] for o in response.json()["data"]["options"]]

    for id in expected_ids:
        assert id in ids

    for id in not_expected_ids:
        assert id not in ids


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
def test_search_with_partial_response_via_soft_failure(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory(org_id=1, items=2, connector_id=1)
    # That tags is not a parseable
    SemanticSearchDocumentFactory(
        org_id=1, tags="oops!", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=relevance&filters={}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 1
    assert response.json()["error"] is True
    assert response.json()["error_code"] == 2001
    assert response.json()["message"] == "Partial results returned"
    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 8

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
def test_search_no_items(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=2"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=relevance&filters={}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 0
    assert "analyticsId" in response.json()["data"]
    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 8

    get_all_connectors_mock.assert_called_once_with(2)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        2, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
def test_search_order_by_alphabetical(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory(
        org_id=1,
        title="abc",
        items__embeddings=[0.05] * embeddings_dimensions,
        items=2,
        connector_id=1,
    )
    SemanticSearchDocumentFactory(
        org_id=1,
        title="cde",
        items__embeddings=[0.5] * embeddings_dimensions,
        items=2,
        connector_id=1,
    )
    SemanticSearchDocumentFactory(
        org_id=1,
        title="bcd",
        items__embeddings=[0.2] * embeddings_dimensions,
        items=2,
        connector_id=1,
    )

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=alphabetical&filters={}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 3
    assert response.json()["data"]["options"][0]["document"]["title"] == "abc"
    assert response.json()["data"]["options"][1]["document"]["title"] == "bcd"
    assert response.json()["data"]["options"][2]["document"]["title"] == "cde"

    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 10

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
def test_search_order_by_alphabetical_multiple_criteria(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory(
        org_id=1, title="bbb", data={"node_id": 333}, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="bbb", data={"node_id": 444}, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="bbb", data={"node_id": 222}, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="ccc", data={"node_id": 111}, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="aaa", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/search?search=test&limit=5&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&sortBy=alphabetical&filters={}",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
    )

    assert response.status_code == 200
    assert len(response.json()["data"]["options"]) == 5

    def is_sorted(arr):
        return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))

    # First item is the mvp
    options = response.json()["data"]["options"][1:]
    titles = [option["document"]["title"] for option in options]
    assert is_sorted(titles)

    for title in list(set(titles)):
        node_ids = [
            option["document"]["data"]["node_id"]
            for option in options
            if option["document"]["title"] == title
            and "node_id" in option["document"]["data"]
        ]
        assert is_sorted(node_ids)

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


def setup_get_suggestions():
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola!", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola Hola!", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_returns_sorted_and_only_requested_org_matches(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    setup_get_suggestions()
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84&limit=5&orgId=1"
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 3
    assert response.json()["data"][0] == "Hola"
    assert response.json()["data"][1] == "Hola!"
    assert response.json()["data"][2] == "Hola Hola!"

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_returns_limited_suggestions(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    setup_get_suggestions()
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&limit=2&orgId=1"
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["data"][0] == "Hola"
    assert response.json()["data"][1] == "Hola!"

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_returns_case_insensitive_suggestions(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    setup_get_suggestions()
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hOLa"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84&limit=2&orgId=1"
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert response.json()["data"][0] == "Hola"
    assert response.json()["data"][1] == "Hola!"

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_returns_deduplicated_suggestions(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    setup_get_suggestions()
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola", items=2, connector_id=1
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        "&limit=5&orgId=1"
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 3
    assert response.json()["data"][0] == "Hola"
    assert response.json()["data"][1] == "Hola!"
    assert response.json()["data"][2] == "Hola Hola!"

    get_all_connectors_mock.assert_called_once_with(1)
    get_search_widget_by_deployment_id_mock.assert_called_once_with(
        1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_is_filtered_by_tags(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    tags = TagParser({"tag-1": ["t1", "t2"]}).to_str()
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola", tags=tags, items=2, connector_id=1
    )
    tags = TagParser({"tag-1": ["t2"], "tag-2": ["a"]}).to_str()
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola!", tags=tags, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    filters = json.dumps({"tags": {"tag-1": ["t1"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola"]

    filters = json.dumps({"tags": {"tag-1": ["t2"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola", "Hola!"]

    filters = json.dumps({"tags": {"tag-1": ["t1", "t2"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola", "Hola!"]

    filters = json.dumps({"tags": {"tag-1": ["t1"], "tag-2": ["a"]}})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola", "Hola!"]

    get_all_connectors_mock.has_calls(
        call(1),
        call(1),
        call(1),
        call(1),
    )
    get_search_widget_by_deployment_id_mock.has_calls(
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_is_filtered_by_connectors(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola", connector_id=1, items=2
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola!", connector_id=2, items=2
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    filters = json.dumps({"connectors": [1]})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=Hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola"]

    filters = json.dumps({"connectors": [1, 2]})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=Hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola", "Hola!"]

    get_all_connectors_mock.has_calls(
        call(1),
        call(1),
    )
    get_search_widget_by_deployment_id_mock.has_calls(
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
    )


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@pytest.mark.usefixtures("refresh_database")
def test_get_suggestions_is_filtered_by_language(
    get_all_connectors_mock, get_search_widget_by_deployment_id_mock
):
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola", language="es", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory(
        org_id=1, title="Hola!", language="en", items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=3, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    filters = json.dumps({"languages": ["es"]})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=Hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola"]

    filters = json.dumps({"languages": ["en"]})
    response = client.get(
        "/ai-service/v1/semantic-search/"
        "suggestions?search=Hola"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
        f"&limit=5&orgId=1&filters={filters}"
    )

    assert response.status_code == 200
    assert response.json()["data"] == ["Hola!"]

    get_all_connectors_mock.has_calls(
        call(1),
        call(1),
    )
    get_search_widget_by_deployment_id_mock.has_calls(
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
    )


@pytest.mark.usefixtures("refresh_database")
def test_get_tags():
    tags = TagParser({"tag-1": ["t1", "t2"]}).to_str()
    SemanticSearchDocumentFactory(org_id=1, tags=tags, items=2)
    tags = TagParser({"tag-1": ["t2"], "tag-2": ["a"]}).to_str()
    SemanticSearchDocumentFactory(org_id=1, tags=tags, items=2)
    SemanticSearchDocumentFactory.create_batch(2, org_id=3, items=2)

    response = client.get("/ai-service/v1/semantic-search/tags?orgId=1")

    assert response.status_code == 200
    assert len(response.json()["data"]) == 2
    assert "tag-1" in response.json()["data"]
    assert len(response.json()["data"]["tag-1"]) == 2
    assert "t1" in response.json()["data"]["tag-1"]
    assert "t2" in response.json()["data"]["tag-1"]
    assert "tag-2" in response.json()["data"]
    assert len(response.json()["data"]["tag-2"]) == 1
    assert "a" in response.json()["data"]["tag-2"]


@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_connectors_by_connector_type_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_connector_types"
)
def test_get_connectors(
    mock_get_connector_types, mock_get_connectors_by_connector_type_id
):
    mock_get_connector_types.return_value = [
        ConnectorType(
            id=1,
            name="ct1",
            provider="ct1",
            description="ct1",
            active=False,
        ),
        ConnectorType(
            id=2,
            name="ct2",
            provider="ct2",
            description="ct2",
            active=True,
        ),
    ]

    mock_get_connectors_by_connector_type_id.return_value = [
        Connector(id=1, name="c1", description="c1", active=True),
        Connector(id=2, name="c2", description="c2", active=False),
    ]

    response = client.get("/ai-service/v1/semantic-search/connectors?orgId=11")

    mock_get_connector_types.assert_called_once_with(org_id=11)
    mock_get_connectors_by_connector_type_id.assert_called_once_with(
        org_id=11, type_id=2
    )

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0] == {
        "id": 1,
        "name": "c1",
        "description": "c1",
        "connectorType": {
            "name": "ct2",
            "description": "ct2",
            "provider": "ct2",
        },
    }


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.core.containers.S3CachedAssetsRepository.get_json_asset")
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@patch("src.adapters.summarizer_client.Llama2SummarizerClient.summarize")
@pytest.mark.usefixtures("refresh_database")
def test_summarize(
    summarize_mock,
    connected_mock,
    embed_mock,
    get_json_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
    make_summarizer_config_plain,
):
    get_json_mock.return_value = make_summarizer_config_plain()
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]
    summarize_mock.return_value = "summary"

    SemanticSearchDocumentFactory.create_batch(
        2, items=2, org_id=1, connector_id=1
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 4
    response = client.get(
        "/ai-service/v1/semantic-search/summarize?query=test&orgId=1"
        "&deploymentId=9a44ad83-a9d2-427d-a8c9-91040d2b6e84"
    )

    assert response.status_code == 200
    assert json.loads(response.content)["data"]["answer"] == "summary"
    assert response.json()["error"] is False
    assert not response.json()["error_code"]
    assert not response.json()["message"]

    get_all_connectors_mock.has_calls(
        call(1),
        call(1),
    )
    get_search_widget_by_deployment_id_mock.has_calls(
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
        call(1, "9a44ad83-a9d2-427d-a8c9-91040d2b6e84"),
    )


def test_get_documents_invalid_requests():
    response = client.get("/ai-service/v1/semantic-search/documents")
    assert response.status_code == 422

    response = client.get(
        "/ai-service/v1/semantic-search/documents?orgId=1&limit=1"
    )
    assert response.status_code == 422

    response = client.get(
        "/ai-service/v1/semantic-search/documents?connectorId=1&offset=1"
    )
    assert response.status_code == 422

    response = client.get(
        "/ai-service/v1/semantic-search/documents?"
        "connectorId=1&offset=1&limit=0"
    )
    assert response.status_code == 422

    response = client.get(
        "/ai-service/v1/semantic-search/documents?"
        "connectorId=1&offset=-1&limit=1"
    )
    assert response.status_code == 422

    response = client.get(
        "/ai-service/v1/semantic-search/documents?"
        "connectorId=1&offset=1&limit=-1"
    )
    assert response.status_code == 422


@pytest.mark.usefixtures("refresh_database")
def test_get_documents_by_org_id():
    SemanticSearchDocumentFactory.create_batch(3, org_id=1, items=2)
    SemanticSearchDocumentFactory.create_batch(2, org_id=2, items=2)

    response = client.get("/ai-service/v1/semantic-search/documents?orgId=1")
    assert len(response.json()["data"]) == 3

    response = client.get("/ai-service/v1/semantic-search/documents?orgId=2")
    assert len(response.json()["data"]) == 2


@pytest.mark.usefixtures("refresh_database")
def test_get_documents_by_connector_id():
    SemanticSearchDocumentFactory.create_batch(3, connector_id=1, items=2)
    SemanticSearchDocumentFactory.create_batch(2, connector_id=2, items=2)

    response = client.get(
        "/ai-service/v1/semantic-search/documents?connectorId=1"
    )
    assert len(response.json()["data"]) == 3

    response = client.get(
        "/ai-service/v1/semantic-search/documents?connectorId=2"
    )
    assert len(response.json()["data"]) == 2


@pytest.mark.usefixtures("refresh_database")
def test_get_documents_paginated():
    docs = SemanticSearchDocumentFactory.create_batch(
        10, connector_id=1, items=2
    )
    SemanticSearchDocumentFactory.create_batch(2, connector_id=2, items=2)

    response = client.get(
        "/ai-service/v1/semantic-search/documents?"
        "connectorId=1&limit=4&offset=2"
    )
    assert len(response.json()["data"]) == 4
    assert response.json()["data"][0]["id"] == docs[2].id
    assert response.json()["data"][1]["id"] == docs[3].id
    assert response.json()["data"][2]["id"] == docs[4].id
    assert response.json()["data"][3]["id"] == docs[5].id

    response = client.get(
        "/ai-service/v1/semantic-search/documents?"
        "connectorId=1&limit=2&offset=3"
    )
    assert len(response.json()["data"]) == 2
    assert response.json()["data"][0]["id"] == docs[3].id
    assert response.json()["data"][1]["id"] == docs[4].id


@pytest.mark.usefixtures("refresh_database")
def test_get_languages():
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, language="en"
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, language="es"
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, language="en"
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, language="es"
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, language="fr"
    )

    response = client.get("/ai-service/v1/semantic-search/languages?orgId=1")
    assert len(response.json()["data"]) == 2

    response = client.get("/ai-service/v1/semantic-search/languages?orgId=2")
    assert len(response.json()["data"]) == 3


@patch(
    "src.repositories.services.config_svc."
    "ConfigSvcRepository.get_search_widget_by_deployment_id"
)
@patch(
    "src.repositories.services.connectors_svc."
    "ConnectorsSvcRepository.get_all_connectors"
)
@patch("src.adapters.embedder_client.CohereEmbedderClient.embed")
@patch("src.adapters.embedder_client.CohereEmbedderClient.connected")
@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
def test_deployment_has_documents(
    connected_mock,
    embed_mock,
    get_all_connectors_mock,
    get_search_widget_by_deployment_id_mock,
):
    connected_mock.return_value = True
    embed_mock.return_value = [[0.1] * embeddings_dimensions]

    SemanticSearchDocumentFactory.create_batch(
        2, org_id=1, items=2, connector_id=1
    )
    SemanticSearchDocumentFactory.create_batch(
        2, org_id=2, items=2, connector_id=3
    )
    w, c1, c2 = widget_mock_data()
    get_all_connectors_mock.return_value = [c1, c2]
    get_search_widget_by_deployment_id_mock.return_value = w

    response = client.get(
        "/ai-service/v1/semantic-search/deployments/"
        "9a44ad83-a9d2-427d-a8c9-91040d2b6e84/"
        "has-documents",
        headers={
            "zt-causer-id": "1",
            "zt-causer-type": "App\\Models\\User",
            "zt-org-id": "1",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"] is True

    response = client.get(
        "/ai-service/v1/semantic-search/deployments/"
        "9a44ad83-a9d2-427d-a8c9-91040d2b6e84/"
        "has-documents",
        headers={
            "zt-causer-id": "1",
            "zt-causer-type": "App\\Models\\User",
            "zt-org-id": "2",
        },
    )
    assert response.status_code == 200
    # Org id doesnt match with the one in the deployment
    assert response.json()["data"] is False

    w.orgId = 2
    get_search_widget_by_deployment_id_mock.return_value = w
    response = client.get(
        "/ai-service/v1/semantic-search/deployments/"
        "9a44ad83-a9d2-427d-a8c9-91040d2b6e84/"
        "has-documents",
        headers={
            "zt-causer-id": "1",
            "zt-causer-type": "App\\Models\\User",
            "zt-org-id": "2",
        },
    )
    assert response.status_code == 200
    # Org id doesnt match with the one in the deployment
    assert response.json()["data"] is False

    w.orgId = 3
    get_search_widget_by_deployment_id_mock.return_value = w
    response = client.get(
        "/ai-service/v1/semantic-search/deployments/"
        "9a44ad83-a9d2-427d-a8c9-91040d2b6e84/"
        "has-documents",
        headers={
            "zt-causer-id": "1",
            "zt-causer-type": "App\\Models\\User",
            "zt-org-id": "3",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"] is False
