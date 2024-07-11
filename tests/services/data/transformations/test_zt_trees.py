import copy
import os
from unittest.mock import ANY, Mock, call, patch

import boto3
import numpy as np
import pytest
from moto import mock_aws

import src.proto.embed_job_status_pb2 as embed_job_status_pb2
from src.core.containers import container
from src.data.chunkers.chunker import CharacterChunker, SentenceChunker
from src.models.semantic_search_item import (
    SemanticSearchDocument,
    SemanticSearchItem,
)
from src.schemas.services.connectors_svc import Connector, ConnectorType
from src.services.data.transformations.zt_trees import (
    BronzeToSilverService,
    RawToBronzeService,
    SilverToGoldService,
)
from src.util.storage import S3Storage
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)
from tests.__stubs__.tree_templates import (
    BRONZE_TREE_TEMPLATE,
    RAW_TREE_TEMPLATE,
    SILVER_TREE_TEMPLATE,
)

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


######################
# Raw To Bronze
######################
@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_raw_to_bronze_zingtree_tree(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "raw/zt_trees/530566/507222858/507222858.json",
        RAW_TREE_TEMPLATE,
        "data-bucket",
    )
    raw_to_bronze_service = RawToBronzeService(s3, Mock())
    path = raw_to_bronze_service.handle(
        "data-bucket",
        "raw/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )
    bucket_files = [
        obj["Key"]
        for obj in s3._client.list_objects_v2(Bucket="data-bucket")["Contents"]
    ]
    assert "bronze/zt_trees/530566/507222858/507222858.json" in bucket_files
    assert (
        path
        == "s3://data-bucket/bronze/zt_trees/530566/507222858/507222858.json"
    )

    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
    notify_mock.assert_called_once_with(
        embed_job_status_pb2.ArticleState.NORMALIZING,
        embed_job_status_pb2.FailureStatus.SUCCESS,
    )


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_raw_to_bronze_zingtree_tree_delete_flow(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket")
    s3.put_json(
        "bronze/zt_trees/530566/507222858/507222858.json",
        RAW_TREE_TEMPLATE,
        "data-bucket",
    )

    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 1

    raw_to_bronze_service = RawToBronzeService(s3, Mock())
    path = raw_to_bronze_service.handle(
        "data-bucket",
        "raw/zt_trees/530566/507222858/507222858.json",
        "Object Deleted",
        "507222858",
        530566,
        1234,
    )

    bucket_files = s3.list_files("data-bucket")
    assert len(bucket_files) == 0
    assert (
        path
        == "s3://data-bucket/bronze/zt_trees/530566/507222858/507222858.json"
    )

    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
    notify_mock.assert_called_once_with(
        embed_job_status_pb2.ArticleState.NORMALIZING,
        embed_job_status_pb2.FailureStatus.SUCCESS,
    )


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_raw_to_bronze_zingtree_tree_with_bucket_and_key_changes(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket-raw")
    s3._client.create_bucket(Bucket="data-bucket-bronze")
    s3.put_json(
        "raw/zt_trees/530566/507222858/507222858.json",
        RAW_TREE_TEMPLATE,
        "data-bucket-raw",
    )
    raw_to_bronze_service = RawToBronzeService(s3, Mock())
    raw_to_bronze_service.handle(
        "data-bucket-raw",
        "raw/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )

    raw_bucket_files = s3.list_files("data-bucket-raw")
    assert len(raw_bucket_files) == 1
    assert "raw/zt_trees/530566/507222858/507222858.json" in raw_bucket_files

    bronze_bucket_files = s3.list_files("data-bucket-bronze")
    assert len(bronze_bucket_files) == 1
    assert (
        "bronze/zt_trees/530566/507222858/507222858.json"
        in bronze_bucket_files
    )

    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
    notify_mock.assert_called_once_with(
        embed_job_status_pb2.ArticleState.NORMALIZING,
        embed_job_status_pb2.FailureStatus.SUCCESS,
    )


# ######################
# # Bronze To Silver
# ######################
@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_bronze_to_silver_zingtree_tree(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")
    s3.put_json(
        "bronze/zt_trees/530566/507222858/507222858.json",
        BRONZE_TREE_TEMPLATE,
        "test-bucket",
    )
    bronze_to_silver_service = BronzeToSilverService(s3, Mock())
    path = bronze_to_silver_service.handle(
        "test-bucket",
        "bronze/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )
    bucket_files = s3.list_files("test-bucket")
    assert len(bucket_files) == 2
    assert "bronze/zt_trees/530566/507222858/507222858.json" in bucket_files
    assert "silver/zt_trees/530566/507222858/507222858.json" in bucket_files
    assert (
        path
        == "s3://test-bucket/silver/zt_trees/530566/507222858/507222858.json"
    )

    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
    notify_mock.assert_not_called()


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_bronze_to_silver_zingtree_tree_delete_flow(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")
    s3.put_json(
        "silver/zt_trees/530566/507222858/507222858.json",
        BRONZE_TREE_TEMPLATE,
        "test-bucket",
    )
    bucket_files = s3.list_files("test-bucket")
    assert len(bucket_files) == 1
    bronze_to_silver_service = BronzeToSilverService(s3, Mock())
    path = bronze_to_silver_service.handle(
        "test-bucket",
        "bronze/zt_trees/530566/507222858/507222858.json",
        "Object Deleted",
        "507222858",
        530566,
        1234,
    )
    bucket_files = s3.list_files("test-bucket")
    assert len(bucket_files) == 0
    assert (
        path
        == "s3://test-bucket/silver/zt_trees/530566/507222858/507222858.json"
    )

    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
    notify_mock.assert_not_called()


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_bronze_to_silver_zingtree_tree_with_bucket_and_key_changes(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="data-bucket-bronze")
    s3._client.create_bucket(Bucket="data-bucket-silver")
    s3.put_json(
        "bronze/zt_trees/530566/507222858/507222858.json",
        BRONZE_TREE_TEMPLATE,
        "data-bucket-bronze",
    )

    bronze_to_silver_service = BronzeToSilverService(s3, Mock())
    bronze_to_silver_service.handle(
        "data-bucket-bronze",
        "bronze/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )

    bronze_bucket_files = s3.list_files("data-bucket-bronze")
    assert len(bronze_bucket_files) == 1
    assert (
        "bronze/zt_trees/530566/507222858/507222858.json"
        in bronze_bucket_files
    )

    silver_bucket_files = s3.list_files("data-bucket-silver")
    assert len(silver_bucket_files) == 1
    assert (
        "silver/zt_trees/530566/507222858/507222858.json"
        in silver_bucket_files
    )
    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
    notify_mock.assert_not_called()


######################
# Silver To Gold
######################
@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_zingtree_tree(set_notifier_data_mock, notify_mock):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")
    s3.put_json(
        "silver/zt_trees/530566/507222858/507222858.json",
        SILVER_TREE_TEMPLATE,
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
            id=1, provider="zingtree", name="", description="", active=True
        )
    ]
    connectors_svc_mock.get_connectors_by_connector_type_id.return_value = [
        Connector(
            id=1, name="zingtree connector", description="", active=True
        ),
    ]

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repo_mock, chunker, connectors_svc_mock
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )

    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 1
    assert repo_mock.create_item.call_count == 2
    repo_mock.create_document.assert_called_once_with(
        "531868",
        "en",
        "Test Tree test title",
        "this is a description",
        ['"zt_trees_trees"."test"', '"zt_trees_trees"."tag"'],
        {
            "node_keywords": ["key", "word"],
            "node_tags": ["tag", "other"],
            "tree_active": True,
            "tree_last_opened": "2023-05-22T18:20:29.000000Z",
            "tree_is_private": False,
            "tree_id": "125365649",
            "display": {"title": "Test Tree", "subtitle": "test title"},
        },
        1,
        "125365649::1",
        "2021-03-04T11:17:03.000000Z",
        "2023-05-22 18:20:28.000000Z",
    )
    repo_mock.create_item.assert_has_calls(
        [
            call(
                ANY,
                "test content of a node Is this a question?",
                "test content of a node Is this a question?",
                inserted_item_mock,
            ),
            call(
                ANY,
                "Test Tree test title",
                "Test Tree test title",
                inserted_item_mock,
            ),
        ]
    )
    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
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


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_zingtree_tree_uses_does_not_create_item_if_it_exists(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")
    s3.put_json(
        "silver/zt_trees/530566/507222858/507222858.json",
        SILVER_TREE_TEMPLATE,
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
            id=1, provider="zingtree", name="", description="", active=True
        )
    ]
    connectors_svc_mock.get_connectors_by_connector_type_id.return_value = [
        Connector(
            id=1, name="zingtree connector", description="", active=True
        ),
    ]

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repo_mock, chunker, connectors_svc_mock
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )

    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 0
    assert repo_mock.create_item.call_count == 2
    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
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


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
def test_silver_to_gold_zingtree_tree_adds_title_for_fully_empty_nodes(
    set_notifier_data_mock,
    notify_mock,
    check_log_message,
):
    s3 = S3Storage(boto3.client("s3"))
    s3._client.create_bucket(Bucket="test-bucket")

    node_json = copy.deepcopy(SILVER_TREE_TEMPLATE)
    node_json["nodes"]["2"] = copy.deepcopy(SILVER_TREE_TEMPLATE["nodes"]["1"])
    node_json["nodes"]["2"]["content"]["content"] = ""
    node_json["nodes"]["2"]["content"]["page_title"] = ""
    node_json["nodes"]["2"]["content"]["question"] = ""

    s3.put_json(
        "silver/zt_trees/530566/507222858/507222858.json",
        node_json,
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
            id=1, provider="zingtree", name="", description="", active=True
        )
    ]
    connectors_svc_mock.get_connectors_by_connector_type_id.return_value = [
        Connector(
            id=1, name="zingtree connector", description="", active=True
        ),
    ]

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repo_mock, chunker, connectors_svc_mock
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/zt_trees/530566/507222858/507222858.json",
        "Object Created",
        "507222858",
        530566,
        1234,
    )

    assert len(ids) == len(node_json["nodes"])
    assert ids == [1, 1]
    assert embedder_mock.embed.call_count == 1
    assert repo_mock.find_document.call_count == 1
    assert repo_mock.create_document.call_count == 1
    assert repo_mock.create_item.call_count == 2
    check_log_message(
        "INFO",
        "[Semantic-Search] Node content,"
        " question, and page_title are empty,"
        " skipping (project_id, project_node_id): (125365649, 2)",
    )
    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
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


@mock_aws
@patch("src.services.data.transformations.base.BaseService._notify")
@patch("src.services.data.transformations.base.BaseService._set_notifier_data")
@pytest.mark.usefixtures("refresh_database")
def test_silver_to_gold_zingtree_tree_delete_flow(
    set_notifier_data_mock, notify_mock
):
    s3 = S3Storage(boto3.client("s3"))
    SemanticSearchDocumentFactory(org_id=1, document_id="2::1", items=1)
    SemanticSearchDocumentFactory(org_id=2, document_id="1::1", items=1)
    repository = container.semantic_search_repository()
    embedder_mock = Mock()
    chunker = SentenceChunker(150, "none")

    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 2
        assert session.query(SemanticSearchDocument).count() == 2

    silver_to_gold_service = SilverToGoldService(
        s3, Mock(), embedder_mock, repository, chunker, Mock()
    )
    ids = silver_to_gold_service.handle(
        "test-bucket",
        "silver/zt_trees/2/1.json",
        "Object Deleted",
        "507222858",
        530566,
        1234,
    )

    assert ids == [2]
    with container.db().session() as session:
        assert session.query(SemanticSearchItem).count() == 1
        assert session.query(SemanticSearchDocument).count() == 1

    set_notifier_data_mock.assert_called_once_with("507222858", 530566, 1234)
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
