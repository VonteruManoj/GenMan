import datetime
import uuid

import pytest

from src.core.containers import container
from src.models.analytics.semantic_search import (
    SemanticSearchAnalytic,
    SemanticSearchAnalyticEvent,
)


@pytest.mark.usefixtures("refresh_mysql_database")
def test_semantic_search_analytic_data_defaults():
    analytic_data = SemanticSearchAnalytic()
    assert analytic_data.id is None
    assert analytic_data.operation is None
    assert analytic_data.created_at is None
    assert analytic_data.causer_id is None
    assert analytic_data.causer_type is None
    assert analytic_data.org_id is None

    analytic_data.operation = "test"
    analytic_data.causer_id = 1
    analytic_data.causer_type = "test"
    analytic_data.org_id = 1
    analytic_data.deployment_id = "123-asd"

    # save a new record
    with container.mysql_db().session() as session:
        session.add(analytic_data)
        session.commit()
        session.refresh(analytic_data)

    assert analytic_data.id is not None
    try:
        uuid.UUID(str(analytic_data.id))
    except ValueError:
        assert False, "analytic_data.id is not a valid UUID"
    assert analytic_data.operation == "test"
    assert analytic_data.created_at is not None
    assert isinstance(analytic_data.created_at, datetime.datetime)
    assert analytic_data.causer_id == 1
    assert analytic_data.causer_type == "test"
    assert analytic_data.org_id == 1


@pytest.mark.usefixtures("refresh_mysql_database")
def test_semantic_search_analytic_data_events_defaults():
    analytic_data = SemanticSearchAnalytic(
        operation="test",
        causer_id=1,
        causer_type="test",
        org_id=1,
        deployment_id="123-asd",
    )

    analytic_data_event = SemanticSearchAnalyticEvent()
    assert analytic_data_event.id is None
    assert analytic_data_event.operation is None
    assert analytic_data_event.created_at is None
    assert analytic_data_event.message is None
    assert analytic_data_event.data is None
    assert analytic_data_event.semantic_search_sessions_id is None

    analytic_data_event.operation = "test"
    analytic_data_event.message = "test"
    analytic_data_event.data = {"test": "test"}

    # save a new record
    with container.mysql_db().session() as session:
        session.add(analytic_data)
        session.commit()
        session.refresh(analytic_data)

        # Foreign key to batch
        analytic_data_event.semantic_search_sessions_id = analytic_data.id

        session.add(analytic_data_event)
        session.commit()
        session.refresh(analytic_data_event)

    assert analytic_data_event.id == 1
    assert analytic_data_event.operation == "test"
    assert analytic_data_event.created_at is not None
    assert isinstance(analytic_data_event.created_at, datetime.datetime)
    assert analytic_data_event.message == "test"
    assert analytic_data_event.data == {"test": "test"}


@pytest.mark.usefixtures("refresh_mysql_database")
def test_semantic_search_analytic_relationships():
    analytic_data = SemanticSearchAnalytic(
        operation="test",
        causer_id=1,
        causer_type="test",
        org_id=1,
        deployment_id="123-asd",
    )

    analytic_data_events = [
        SemanticSearchAnalyticEvent(
            operation="test",
            message="test",
            data={"test": "test"},
        ),
        SemanticSearchAnalyticEvent(
            operation="test2",
            message="test2",
            data={"test2": "test2"},
        ),
    ]
    analytic_data.events.extend(analytic_data_events)

    with container.mysql_db().session() as session:
        session.add(analytic_data)
        session.commit()
        session.refresh(analytic_data)

    assert len(analytic_data.events) == 2
    assert (
        analytic_data.events[0].semantic_search_sessions_id == analytic_data.id
    )
