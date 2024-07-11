import uuid

import pytest

from src.core.containers import container
from src.models.analytics.semantic_search import (
    SemanticSearchAnalytic,
    SemanticSearchAnalyticEvent,
)
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_create_batch():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch = semantic_search_analytics_repository.create_batch(
        operation="test",
        deployment_id="test-123456",
    )

    assert batch.operation == "test"
    assert batch.causer_id == 1
    assert batch.causer_type == "user"
    assert batch.org_id == 4


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_append_event_to_batch():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch = semantic_search_analytics_repository.create_batch(
        operation="test",
        deployment_id="test-123456",
    )

    event = semantic_search_analytics_repository.append_event_to_batch(
        batch=batch,
        operation="test1",
        message="test2",
        data={"test3": "test4"},
    )

    assert batch.id == event.semantic_search_sessions_id
    assert event.operation == "test1"
    assert event.message == "test2"
    assert event.data == {"test3": "test4"}


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_find_batch_by_id():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch = semantic_search_analytics_repository.create_batch(
        operation="test",
        deployment_id="test-123456",
    )

    batch_find = semantic_search_analytics_repository.find_batch_by_id(
        id=batch.id,
    )

    assert batch.id == batch_find.id
    assert batch.operation == batch_find.operation
    assert batch.causer_id == batch_find.causer_id
    assert batch.causer_type == batch_find.causer_type
    assert batch.org_id == batch_find.org_id


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_find_batch_by_id_not_found():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch_find = semantic_search_analytics_repository.find_batch_by_id(
        id=uuid.uuid1(),
    )

    assert batch_find is None


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_find_batch_by_id_with_non_uuid_returns_none():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch_find = semantic_search_analytics_repository.find_batch_by_id(
        id="1",
    )

    assert batch_find is None


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_find_batch_by_id_different_causer_id_not_found():
    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch = semantic_search_analytics_repository.create_batch(
        operation="test",
        deployment_id="test-123456",
    )

    container.audit_repository().data.causer_id = 2

    batch_find = semantic_search_analytics_repository.find_batch_by_id(
        id=batch.id,
    )

    assert batch_find is None


@pytest.mark.usefixtures("refresh_mysql_database")
@pytest.mark.usefixtures("mock_audit_in_memory")
def test_start_analytics_batch_from_search():
    documents = SemanticSearchDocumentFactory.create_batch(
        2, items=2, org_id=1
    )
    options = [documents[0].items[0], documents[1].items[0]]
    distances = len(options) * [0]

    # Attach options to session
    with container.db().session() as session:
        session.add_all(options)
        session.commit()
        for option in options:
            session.refresh(option)

    semantic_search_analytics_repository = (
        container.semantic_search_analytics_repository()
    )

    batch = semantic_search_analytics_repository.from_search(
        search="test text",
        filters={
            "tags": {
                "tag-1": ["v1"],
            }
        },
        limit=10,
        sort_by="test sort",
        options=options,
        distances=distances,
        deployment_id="test-123456",
    )

    assert batch.operation == "search"
    assert batch.causer_id == 1  # from mock audit
    assert batch.causer_type == "user"  # from mock audit
    assert batch.org_id == 4  # from mock audit
    event = batch.events[0]
    assert event.operation == "search"
    assert event.message == "Found 2 options for test text"
    assert event.data == {
        "request": {
            "query": "test text",
            "limit": 10,
            "sort_by": "test sort",
            "filters": {
                "tags": {
                    "tag-1": ["v1"],
                }
            },
        },
        "options": [
            {**options[0].to_analytics_dict(), "distance": 0},
            {**options[1].to_analytics_dict(), "distance": 0},
        ],
    }
    with container.mysql_db().session() as session:
        # assert there is only 1 batch in the database
        assert session.query(SemanticSearchAnalytic).count() == 1
        # assert there is only 1 event in the database
        assert session.query(SemanticSearchAnalyticEvent).count() == 1
