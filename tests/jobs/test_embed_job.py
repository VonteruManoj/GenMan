from unittest.mock import ANY, patch

import mock

import src.proto.embed_jobs_pb2 as embed_jobs_pb2
from src.exceptions.transformations import NotifiedException
from src.jobs.embed_job import EmbedJob


def zt_notification(action=0):
    event = embed_jobs_pb2.ArticleNotification()
    event.id = "id_1"
    event.articleId = "101868944"
    event.connectorId = 5
    event.orgId = 789789
    event.source = "zingtree"
    event.timestamp = 123
    event.operation = action
    event.location.bucket = "some-bucket"
    event.location.region = "us-east-1"
    event.location.path = "raw/zt_trees/789789/101868944"
    event.jobId = "TheJobID123"

    return event


def sfk_notification(action=0):
    event = embed_jobs_pb2.ArticleNotification()
    event.id = "id_2"
    event.articleId = "kA05j000001ZBKrCAO"
    event.connectorId = 6
    event.orgId = 789789
    event.source = "salesforce"
    event.timestamp = 123
    event.operation = action
    event.location.bucket = "some-bucket"
    event.location.region = "us-east-1"
    event.location.path = "bronze/articles/789789"
    event.jobId = "TheJobID456"

    return event


@patch("src.jobs.embed_job.container")
def test_zingtree_orchestrator_insert(container_mock):
    container_mock.zt_trees_raw_to_bronze_service().handle.return_value = (
        "s3://some-bucket/bronze/zt_trees/789789/101868944/101868944.json"
    )

    container_mock.zt_trees_bronze_to_silver_service().handle.return_value = (
        "s3://some-bucket/silver/zt_trees/789789/101868944/101868944.json"
    )

    job = EmbedJob()
    job.run(zt_notification(0))

    container_mock.zt_trees_raw_to_bronze_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )

    container_mock.zt_trees_raw_to_bronze_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "raw/zt_trees/789789/101868944/101868944.json",
        "Object Created",
        "101868944",
        789789,
        5,
    )

    container_mock.zt_trees_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/zt_trees/789789/101868944/101868944.json",
        "Object Created",
        "101868944",
        789789,
        5,
    )

    container_mock.zt_trees_silver_to_gold_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_silver_to_gold_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "silver/zt_trees/789789/101868944/101868944.json",
        "Object Created",
        "101868944",
        789789,
        5,
    )


@patch("src.jobs.embed_job.container")
def test_zingtree_orchestrator_update(container_mock):
    container_mock.zt_trees_raw_to_bronze_service().handle.return_value = (
        "s3://some-bucket/bronze/zt_trees/789789/101868944/101868944.json"
    )

    container_mock.zt_trees_bronze_to_silver_service().handle.return_value = (
        "s3://some-bucket/silver/zt_trees/789789/101868944/101868944.json"
    )

    job = EmbedJob()
    job.run(zt_notification(1))

    container_mock.zt_trees_raw_to_bronze_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_raw_to_bronze_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "raw/zt_trees/789789/101868944/101868944.json",
        "Object Created",
        "101868944",
        789789,
        5,
    )

    container_mock.zt_trees_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/zt_trees/789789/101868944/101868944.json",
        "Object Created",
        "101868944",
        789789,
        5,
    )

    container_mock.zt_trees_silver_to_gold_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_silver_to_gold_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "silver/zt_trees/789789/101868944/101868944.json",
        "Object Created",
        "101868944",
        789789,
        5,
    )


@patch("src.jobs.embed_job.container")
def test_zingtree_orchestrator_delete(container_mock):
    container_mock.zt_trees_raw_to_bronze_service().handle.return_value = (
        "s3://some-bucket/bronze/zt_trees/789789/101868944/101868944.json"
    )

    container_mock.zt_trees_bronze_to_silver_service().handle.return_value = (
        "s3://some-bucket/silver/zt_trees/789789/101868944/101868944.json"
    )

    job = EmbedJob()
    job.run(zt_notification(2))

    container_mock.zt_trees_raw_to_bronze_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_raw_to_bronze_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "raw/zt_trees/789789/101868944/101868944.json",
        "Object Deleted",
        "101868944",
        789789,
        5,
    )

    container_mock.zt_trees_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/zt_trees/789789/101868944/101868944.json",
        "Object Deleted",
        "101868944",
        789789,
        5,
    )

    container_mock.zt_trees_silver_to_gold_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID123",
    )
    container_mock.zt_trees_silver_to_gold_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "silver/zt_trees/789789/101868944/101868944.json",
        "Object Deleted",
        "101868944",
        789789,
        5,
    )


@patch("src.jobs.embed_job.container")
def test_article_orchestrator_insert(container_mock):
    container_mock.article_kb_bronze_to_silver_service().handle.return_value = {  # noqa: E501
        "bucket": "some-bucket",
        "key": "bronze/articles/789789/kA05j000001ZBKrCAO.json",
        "connector_id": "some",
        "detail_type": "Object Created",
    }

    job = EmbedJob()
    job.run(sfk_notification(0))

    container_mock.article_kb_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789",
        "kA05j000001ZBKrCAO",
        789789,
        6,
        "insert",
    )

    container_mock.article_kb_silver_to_gold_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_silver_to_gold_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789/kA05j000001ZBKrCAO.json",
        "some",
        "Object Created",
        "kA05j000001ZBKrCAO",
        789789,
    )


@patch("src.jobs.embed_job.container")
def test_article_orchestrator_update(container_mock):
    container_mock.article_kb_bronze_to_silver_service().handle.return_value = {  # noqa: E501
        "bucket": "some-bucket",
        "key": "bronze/articles/789789/kA05j000001ZBKrCAO.json",
        "connector_id": "some",
        "detail_type": "Object Created",
    }

    job = EmbedJob()
    job.run(sfk_notification(1))

    container_mock.article_kb_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789",
        "kA05j000001ZBKrCAO",
        789789,
        6,
        "update",
    )

    container_mock.article_kb_silver_to_gold_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_silver_to_gold_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789/kA05j000001ZBKrCAO.json",
        "some",
        "Object Created",
        "kA05j000001ZBKrCAO",
        789789,
    )


@patch("src.jobs.embed_job.container")
def test_article_orchestrator_delete(container_mock):
    container_mock.article_kb_bronze_to_silver_service().handle.return_value = {  # noqa: E501
        "bucket": "some-bucket",
        "key": "bronze/articles/789789/kA05j000001ZBKrCAO.json",
        "connector_id": "some",
        "detail_type": "Object Deleted",
    }

    job = EmbedJob()
    job.run(sfk_notification(2))

    container_mock.article_kb_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789",
        "kA05j000001ZBKrCAO",
        789789,
        6,
        "delete",
    )

    container_mock.article_kb_silver_to_gold_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_silver_to_gold_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789/kA05j000001ZBKrCAO.json",
        "some",
        "Object Deleted",
        "kA05j000001ZBKrCAO",
        789789,
    )


@patch("src.jobs.embed_job.container")
def test_article_orchestrator_silver_to_gold_disabled(container_mock):
    container_mock.article_kb_bronze_to_silver_service().handle.return_value = (  # noqa: E501
        None
    )

    job = EmbedJob()
    job.run(sfk_notification(2))

    container_mock.article_kb_bronze_to_silver_service().set_job_id.assert_called_once_with(  # noqa: E501
        "TheJobID456",
    )
    container_mock.article_kb_bronze_to_silver_service().handle.assert_called_once_with(  # noqa: E501
        "some-bucket",
        "bronze/articles/789789",
        "kA05j000001ZBKrCAO",
        789789,
        6,
        "delete",
    )

    container_mock.article_kb_silver_to_gold_service().set_job_id.assert_not_called()  # noqa: E501
    container_mock.article_kb_silver_to_gold_service().handle.assert_not_called()  # noqa: E501


@patch("src.jobs.embed_job.container")
def test_orchestrator_notfied_failure_should_not_notify(container_mock):
    container_mock.article_kb_bronze_to_silver_service().handle.side_effect = (
        NotifiedException("Mocked error")
    )
    producer_mock = mock.Mock()
    producer_mock.produce.return_value = None

    job = EmbedJob(producer_mock)
    job.run(sfk_notification())

    producer_mock.produce.assert_not_called()


@patch("src.jobs.embed_job.container")
def test_orchestrator_failure(container_mock, check_log_message):
    container_mock.article_kb_bronze_to_silver_service().handle.side_effect = (
        ValueError("Mocked error")
    )
    producer_mock = mock.Mock()
    producer_mock.produce.return_value = None

    job = EmbedJob(producer_mock)
    job.run(sfk_notification())

    check_log_message("ERROR", "Error processing event: Mocked error")

    # TODO: due to durration we need to mokey
    # patch time.time() to return stable value
    # example: b"\n\x12kA05j000001ZBKrCAO\x10\x9d\x9a0\x18\x06 \x01(\x0c0\x01:\x0cMocked errorB\x0bTheJobID456",  # noqa: E501
    producer_mock.produce.assert_called_once_with(
        "embed-job-status-local-test", ANY, key="TheJobID456"
    )
