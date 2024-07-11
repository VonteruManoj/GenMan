import copy
import os
from unittest.mock import Mock

import boto3
import numpy as np
import pytest
from moto import mock_aws

from src.core.containers import container
from src.data.chunkers.chunker import CharacterChunker
from src.models.semantic_search_item import (
    SemanticSearchDocument,
    SemanticSearchItem,
)
from src.schemas.services.connectors_svc import Connector, ConnectorType
from src.services.data.transformations.html import SilverToGoldService
from src.util.storage import S3Storage
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)
from tests.__stubs__.html_templates import SILVER_HTML_TEMPLATE

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


@mock_aws
def test_silver_to_gold_html():
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")
    s3.put_json(
        "silver/html/530566/507222858.json",
        SILVER_HTML_TEMPLATE,
        "test-bucket",
    )
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.zeros(embeddings_dimensions)
    repo_mock = Mock()
    repo_mock.create_item = Mock()
    repo_mock.create_document = Mock()
    inserted_item_mock = Mock()
    inserted_item_mock.id = 1
    repo_mock.create_item.return_value = inserted_item_mock
    repo_mock.find_document.return_value = None
    repo_mock.create_document.return_value = inserted_item_mock
    chunker = CharacterChunker(150, "none")
    connectors_svc_mock = Mock()
    connectors_svc_mock.get_connector_types.return_value = [
        ConnectorType(
            id=1, provider="html", name="", description="", active=True
        )
    ]
    connectors_svc_mock.get_connectors_by_connector_type_id.return_value = [
        Connector(id=1, name="html connector", description="", active=True),
    ]
    silver_to_gold_service = SilverToGoldService(
        s3, embedder_mock, repo_mock, chunker, connectors_svc_mock
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/html/530566/507222858.json",
        "Object Created",
    )

    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 1
    assert repo_mock.create_item.call_count == 2
    repo_mock.create_document.assert_called_once_with(
        "530566",
        "en",
        "Testing text",
        None,
        [],
        {
            "content": "THIS IS AN amazing text written for the"
            " purpose of testing and it is very very"
            " long because it is for testing",
            "url": "amazing.website.com/amazing-page",
            "type": "HTML",
            "description": None,
        },
        1,
        "736661-amazing-page",
        None,
        None,
    )


@mock_aws
def test_silver_to_gold_html_uses_does_not_create_item_if_it_exists():
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")
    s3.put_json(
        "silver/html/530566/123456/507222858/507222858.json",
        SILVER_HTML_TEMPLATE,
        "test-bucket",
    )
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.zeros(embeddings_dimensions)
    repo_mock = Mock()
    repo_mock.create_item = Mock()
    repo_mock.create_document = Mock()
    inserted_item_mock = Mock()
    inserted_item_mock.id = 1
    repo_mock.create_item.return_value = inserted_item_mock
    repo_mock.find_document.return_value = inserted_item_mock
    repo_mock.create_document.return_value = inserted_item_mock
    chunker = CharacterChunker(150, "none")
    connectors_svc_mock = Mock()
    connectors_svc_mock.get_connector_types.return_value = [
        ConnectorType(
            id=1, provider="html", name="", description="", active=True
        )
    ]
    connectors_svc_mock.get_connectors_by_connector_type_id.return_value = [
        Connector(id=1, name="html connector", description="", active=True),
    ]

    silver_to_gold_service = SilverToGoldService(
        s3, embedder_mock, repo_mock, chunker, connectors_svc_mock
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/html/530566/123456/507222858/507222858.json",
        "Object Created",
    )

    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 0
    assert repo_mock.create_item.call_count == 2


@mock_aws
def test_silver_to_gold_html_skips_fully_empty_files(check_log_message):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")

    html_json = copy.deepcopy(SILVER_HTML_TEMPLATE)
    html_json["content"] = ""
    html_json["title"] = ""

    s3.put_json(
        "silver/html/530566/123456/507222858/507222858.json",
        html_json,
        "test-bucket",
    )
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.zeros(embeddings_dimensions)
    repo_mock = Mock()
    repo_mock.create_item = Mock()
    repo_mock.create_document = Mock()
    inserted_item_mock = Mock()
    inserted_item_mock.id = 1
    repo_mock.create_item.return_value = inserted_item_mock
    repo_mock.find_document.return_value = None
    repo_mock.create_document.return_value = inserted_item_mock
    chunker = CharacterChunker(150, "none")
    connectors_svc_mock = Mock()
    connectors_svc_mock.get_connector_types.return_value = [
        ConnectorType(
            id=1, provider="html", name="", description="", active=True
        )
    ]
    connectors_svc_mock.get_connectors_by_connector_type_id.return_value = [
        Connector(id=1, name="html connector", description="", active=True),
    ]

    silver_to_gold_service = SilverToGoldService(
        s3, embedder_mock, repo_mock, chunker, connectors_svc_mock
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/html/530566/123456/507222858/507222858.json",
        "Object Created",
    )

    assert len(ids) == 0
    assert ids == []
    assert embedder_mock.embed.call_count == 0
    assert repo_mock.find_document.call_count == 0
    assert repo_mock.create_document.call_count == 0
    assert repo_mock.create_item.call_count == 0
    check_log_message(
        "INFO",
        "[Semantic-Search] HTML content, and title are empty, "
        "skipping (html_id): (736661-amazing-page)",
    )


@mock_aws
@pytest.mark.usefixtures("refresh_database")
def test_silver_to_gold_html_delete_flow():
    s3 = S3Storage(boto3.client("s3"))
    repository = container.semantic_search_repository()

    SemanticSearchDocumentFactory(org_id=1, document_id="123-id", items=1)
    SemanticSearchDocumentFactory(org_id=2, items=1)

    embedder_mock = Mock()
    chunker = CharacterChunker(150, "none")

    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 2
        assert session.query(SemanticSearchDocument).count() == 2

    silver_to_gold_service = SilverToGoldService(
        s3, embedder_mock, repository, chunker, Mock()
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/html/1/123-id.json",
        "Object Deleted",
    )

    assert ids == [1]
    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 1
        assert session.query(SemanticSearchDocument).count() == 1
