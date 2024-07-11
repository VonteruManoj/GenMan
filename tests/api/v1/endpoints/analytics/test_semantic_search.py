import json

import pytest
from fastapi.testclient import TestClient

from src.core.containers import container
from src.main import app
from src.models.analytics.semantic_search import (
    SemanticSearchAnalytic,
    SemanticSearchAnalyticEvent,
)

client = TestClient(app)


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_append_event_to_event_not_found():
    response = client.post(
        "/ai-service/v1/analytics/"
        "semantic-search/550e8400-e29b-41d4-a716-446655440000",
        headers={"zt-causer-id": "1", "zt-causer-type": "App\\Models\\User"},
        json={
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
        },
    )

    assert response.status_code == 404
    assert response.json()["error"] is True
    assert response.json()["error_code"] == 4040
    assert response.json()["message"] == "Batch not found"


@pytest.mark.usefixtures("refresh_database")
@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_append_event():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )
    batch = semantic_search_analytics_repository.create_batch(
        operation="test",
        deployment_id="test-123456",
    )

    response = client.post(
        f"/ai-service/v1/analytics/semantic-search/{batch.id}",
        headers={
            "zt-causer-id": "1",
            "zt-causer-type": "user",
            "ZT-Org-Id": "4",
        },
        json={
            "operation": "user_click",
            "message": "User click in a result.",
            "deployment_id": "test-123456",
            "data": json.dumps(
                {
                    "link": "http://example.com",
                    "node_id": 1,
                    "project_id": 1,
                    "result_order": 2,
                    "sort_by": "relevance",
                }
            ),
        },
    )

    assert response.status_code == 200
    assert response.json()["error"] is False
    assert response.json()["error_code"] is None
    assert response.json()["message"] == "Event appended to batch successfully"

    with container.mysql_db().session() as session:
        # assert there is only 1 batch in the database
        assert session.query(SemanticSearchAnalytic).count() == 1
        # assert there is only 1 event in the database
        assert session.query(SemanticSearchAnalyticEvent).count() == 1

        session.add(batch)
        session.refresh(batch)

    assert len(batch.events) == 1
    assert batch.events[0].operation == "user_click"
    assert batch.events[0].message == "User click in a result."
    assert batch.events[0].data == {
        "link": "http://example.com",
        "node_id": 1,
        "project_id": 1,
        "result_order": 2,
        "sort_by": "relevance",
    }
