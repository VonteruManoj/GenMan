import copy
import os
from unittest.mock import Mock, call, patch

import boto3
import numpy as np
import pytest
from moto import mock_aws

import src.proto.embed_job_status_pb2 as embed_job_status_pb2
from src.core.containers import container
from src.data.chunkers.chunker import CharacterChunker
from src.models.semantic_search_item import (
    SemanticSearchDocument,
    SemanticSearchItem,
)
from src.services.data.transformations.article_kb import (
    BronzeToSilverService,
    SilverToGoldService,
)
from src.util.storage import S3Storage
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)
from tests.__stubs__.article_kb_templates import (
    BRONZE_SALESFORCE_KB_TEMPLATE,
    SILVER_SALESFORCE_KB_TEMPLATE,
)

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


@patch(
    "src.services.data.transformations.article_kb.BronzeToSilverService"
    "._insert"
)
@patch(
    "src.services.data.transformations.article_kb.BronzeToSilverService"
    "._update"
)
@patch(
    "src.services.data.transformations.article_kb.BronzeToSilverService"
    "._delete"
)
def test_service_calls_correct_function(delete_mock, update_mock, insert_mock):
    bronze_to_silver_service = BronzeToSilverService(Mock(), Mock(), "", True)
    bucket = "test-bucket"
    path = "test/path"
    filename = "test-key.json"
    org_id = 1
    connector_id = 2
    bronze_to_silver_service.handle(
        bucket,
        path,
        filename,
        org_id,
        connector_id,
        BronzeToSilverService.OP_INSERT,
    )
    insert_mock.assert_called_once_with(
        bucket,
        path,
        filename,
        org_id,
        connector_id,
    )
    bronze_to_silver_service.handle(
        bucket,
        path,
        filename,
        org_id,
        connector_id,
        BronzeToSilverService.OP_UPDATE,
    )
    update_mock.assert_called_once_with(
        bucket, path, filename, org_id, connector_id
    )
    bronze_to_silver_service.handle(
        bucket,
        path,
        filename,
        org_id,
        connector_id,
        BronzeToSilverService.OP_DELETE,
    )
    delete_mock.assert_called_once_with(
        bucket,
        path,
        filename,
        org_id,
        connector_id,
    )


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_bronze_to_silver_insert_service(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "bronze/article_kb/530566/507222858.json",
        BRONZE_SALESFORCE_KB_TEMPLATE,
        "data-bucket",
    )
    bronze_to_silver_service = BronzeToSilverService(
        s3, Mock(), "https://localhost", True
    )
    response = bronze_to_silver_service.handle(
        "data-bucket",
        "bronze/article_kb/530566/",
        "507222858",
        530566,
        123456,
        BronzeToSilverService.OP_INSERT,
    )
    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 2
    assert "bronze/article_kb/530566/507222858.json" in bucket_files
    output_path = "silver/article_kb/530566/507222858.json"
    assert output_path in bucket_files
    transformed = s3.get_json(output_path, "data-bucket")
    assert transformed == SILVER_SALESFORCE_KB_TEMPLATE

    notify_mock.assert_called_once_with(
        embed_job_status_pb2.ArticleState.NORMALIZING,
        embed_job_status_pb2.FailureStatus.SUCCESS,
    )
    set_notifier_data_mock.assert_called_once_with(
        "507222858",
        530566,
        123456,
    )
    assert response == {
        "bucket": "data-bucket",
        "key": "silver/article_kb/530566/507222858.json",
        "connector_id": 123456,
        "detail_type": "Object Created",
    }


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_bronze_to_silver_update_service(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    data = copy.deepcopy(BRONZE_SALESFORCE_KB_TEMPLATE)
    data["tags"].append({"name": "test-tag", "values": ["tag-1", "tag-2"]})
    s3.put_json(
        "bronze/article_kb/530566/507222858.json",
        data,
        "data-bucket",
    )
    s3.put_json(
        "silver/article_kb/530566/507222858.json",
        SILVER_SALESFORCE_KB_TEMPLATE,
        "data-bucket",
    )

    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 2

    bronze_to_silver_service = BronzeToSilverService(
        s3, Mock(), "https://localhost/", True
    )
    response = bronze_to_silver_service.handle(
        "data-bucket",
        "bronze/article_kb/530566/",
        "507222858",
        530566,
        123456,
        BronzeToSilverService.OP_INSERT,
    )

    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 2

    assert "bronze/article_kb/530566/507222858.json" in bucket_files
    output_path = "silver/article_kb/530566/507222858.json"
    assert output_path in bucket_files

    transformed = s3.get_json(output_path, "data-bucket")
    assert len(transformed["tags"]) == 4
    assert '"test-tag"."tag-1"' in transformed["tags"]
    assert '"test-tag"."tag-2"' in transformed["tags"]

    notify_mock.assert_called_once_with(
        embed_job_status_pb2.ArticleState.NORMALIZING,
        embed_job_status_pb2.FailureStatus.SUCCESS,
    )
    set_notifier_data_mock.assert_called_once_with(
        "507222858",
        530566,
        123456,
    )
    assert response == {
        "bucket": "data-bucket",
        "key": "silver/article_kb/530566/507222858.json",
        "connector_id": 123456,
        "detail_type": "Object Created",
    }


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_bronze_to_silver_delete_service(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "bronze/article_kb/530566/507222858.json",
        BRONZE_SALESFORCE_KB_TEMPLATE,
        "data-bucket",
    )

    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 1

    bronze_to_silver_service = BronzeToSilverService(
        s3, Mock(), "https://localhost/", True
    )
    response = bronze_to_silver_service.handle(
        "data-bucket",
        "bronze/article_kb/530566/",
        "507222858",
        530566,
        123456,
        BronzeToSilverService.OP_DELETE,
    )

    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 0

    # NOTE: notify param is always false for _delete
    # notify_mock.assert_called_once_with(
    #     embed_job_status_pb2.ArticleState.NORMALIZING,
    #     embed_job_status_pb2.FailureStatus.SUCCESS,
    # )
    set_notifier_data_mock.assert_called_once_with(
        "507222858",
        530566,
        123456,
    )
    assert response == {
        "bucket": "data-bucket",
        "key": "silver/article_kb/530566/507222858.json",
        "connector_id": 123456,
        "detail_type": "Object Deleted",
    }


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_service_service(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "silver/article_kb/530566/507222858.json",
        SILVER_SALESFORCE_KB_TEMPLATE,
        "data-bucket",
    )
    embedder_mock = Mock()
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

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repo_mock, chunker
    )
    ids = silver_to_gold_service.handle(
        "data-bucket",
        "silver/article_kb/530566/507222858.json",
        123456,
        "Object Created",
        "507222858",
        530566,
    )

    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 1
    assert repo_mock.create_item.call_count == 2
    repo_mock.create_document.assert_called_once_with(
        "530566",
        "en-US",
        "Os-Information",
        None,
        [
            '"Support_Options"."Support Options"',
            '"Product_Support"."Product Support"',
        ],
        {
            "version": 1,
            "articleNumber": "000001001",
            "contentType": "text/html",
            "articleType": "Knowledge__kav",
            "filePath": "",
            "publishedAt": "0001-01-01T00:00:00+00:00",
        },
        123456,
        "kA05j000001YlfWCAS",
        "2023-09-11T08:59:52+00:00",
        "2023-09-11T10:54:06+00:00",
    )

    notify_mock.assert_has_calls(
        [
            call(
                embed_job_status_pb2.ArticleState.EMBEDDING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
            call(
                embed_job_status_pb2.ArticleState.COMPLETE,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
        ]
    )
    set_notifier_data_mock.assert_called_once_with(
        "507222858",
        530566,
        123456,
    )


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_does_not_create_item_if_it_exists(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "silver/article_kb/530566/507222858.json",
        SILVER_SALESFORCE_KB_TEMPLATE,
        "data-bucket",
    )
    embedder_mock = Mock()
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

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repo_mock, chunker
    )
    ids = silver_to_gold_service.handle(
        "data-bucket",
        "silver/article_kb/530566/507222858.json",
        123456,
        "Object Created",
        "507222858",
        530566,
    )

    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 0
    assert repo_mock.create_item.call_count == 2

    notify_mock.assert_has_calls(
        [
            call(
                embed_job_status_pb2.ArticleState.EMBEDDING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
            call(
                embed_job_status_pb2.ArticleState.COMPLETE,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
        ]
    )
    set_notifier_data_mock.assert_called_once_with(
        "507222858",
        530566,
        123456,
    )


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_skips_fully_emtpy_files(
    set_notifier_data_mock, notify_mock, check_log_message
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")

    silver_json = copy.deepcopy(SILVER_SALESFORCE_KB_TEMPLATE)
    silver_json["content"] = ""
    silver_json["title"] = ""

    s3.put_json(
        "silver/article_kb/530566/507222858.json",
        silver_json,
        "data-bucket",
    )
    embedder_mock = Mock()
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

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repo_mock, chunker
    )
    ids = silver_to_gold_service.handle(
        "data-bucket",
        "silver/article_kb/530566/507222858.json",
        123456,
        "Object Created",
        "507222858",
        530566,
    )

    assert len(ids) == 0
    assert ids == []
    assert embedder_mock.embed.call_count == 0
    assert repo_mock.find_document.call_count == 0
    assert repo_mock.create_document.call_count == 0
    assert repo_mock.create_item.call_count == 0
    check_log_message(
        "INFO",
        "[Semantic-Search] Salesforce content, and title are empty, skipping "
        "(document_id): (kA05j000001YlfWCAS)",
    )

    notify_mock.assert_has_calls(
        [
            call(
                embed_job_status_pb2.ArticleState.EMBEDDING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
            call(
                embed_job_status_pb2.ArticleState.COMPLETE,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
        ]
    )
    set_notifier_data_mock.assert_called_once_with(
        "507222858",
        530566,
        123456,
    )


@mock_aws
@pytest.mark.usefixtures("refresh_database")
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_delete_flow(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "silver/article_kb/2/doc-2.json",
        SILVER_SALESFORCE_KB_TEMPLATE,
        "data-bucket",
    )

    repository = container.semantic_search_repository()

    SemanticSearchDocumentFactory(org_id=1, document_id="doc-1", items=1)
    SemanticSearchDocumentFactory(org_id=2, document_id="doc-2", items=1)

    embedder_mock = Mock()
    chunker = CharacterChunker(150, "none")

    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 2
        assert session.query(SemanticSearchDocument).count() == 2
    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 1

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repository, chunker
    )
    ids = silver_to_gold_service.handle(
        "data-bucket",
        "silver/article_kb/2/doc-2.json",
        123456,
        "Object Deleted",
        "doc-2",
        2,
    )

    assert ids == [2]
    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 1
        assert session.query(SemanticSearchDocument).count() == 1
    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 0

    notify_mock.assert_has_calls(
        [
            call(
                embed_job_status_pb2.ArticleState.COMPLETE,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            ),
        ]
    )
    set_notifier_data_mock.assert_called_once_with(
        "doc-2",
        2,
        123456,
    )
