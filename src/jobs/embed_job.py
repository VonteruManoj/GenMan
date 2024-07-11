import json
import os
import time

import src.proto.embed_job_status_pb2 as embed_job_status_pb2
import src.proto.embed_jobs_pb2 as embed_jobs_pb2
import src.services.data.transformations.article_kb as article_kb
from src.contracts.events import EventProducerInterface
from src.core.config import get_settings
from src.core.containers import container
from src.core.deps.logger import with_logger
from src.exceptions.transformations import NotifiedException


@with_logger()
class EmbedJob:
    def __init__(
        self,
        event_producer: EventProducerInterface = None,
    ) -> None:
        self._event_producer = event_producer

    def _notify_failure(
        self,
        article: embed_jobs_pb2.ArticleNotification,
        error: str,
        started_at: float,
    ):
        if self._event_producer is None:
            self._logger.error(
                "No event producer configured, "
                "skipping notification for job status"
            )
            return

        s = embed_job_status_pb2.NotificationResponse()
        s.id = article.articleId
        s.orgId = article.orgId
        s.connectorId = article.connectorId
        s.dur = int((time.time() - started_at) * 1000)
        s.state = embed_job_status_pb2.ArticleState.COMPLETE
        s.status = embed_job_status_pb2.FailureStatus.FAILED
        s.reason = error
        s.jobId = self.event.jobId

        self._event_producer.produce(
            get_settings().KAFKA_EMBED_JOB_STATUS_TOPIC,
            s.SerializeToString(),
            key=self.event.jobId,
        )
        self._logger.info(f"Notifying job status: " f"{json.dumps(str(s))}")

    def run_zingtree(self):
        def parse_location(location: str):
            segments = location.replace("s3://", "").split("/")
            bucket = segments[0]
            segments.pop(0)
            path = "/".join(segments)
            return bucket, path

        self._logger.info("Zingtree article syncying process strated")

        event = "Object Created"
        if self.event.operation == embed_jobs_pb2.ArticleOperation.DELETE:
            event = "Object Deleted"

        filepath = os.path.join(
            self.event.location.path, f"{self.event.articleId}.json"
        )

        zt_trees_raw_to_bronze_service = (
            container.zt_trees_raw_to_bronze_service()
        )
        zt_trees_raw_to_bronze_service.set_job_id(self.event.jobId)
        filename = zt_trees_raw_to_bronze_service.handle(
            self.event.location.bucket,
            filepath,
            event,
            self.event.articleId,
            self.event.orgId,
            self.event.connectorId,
        )
        self._logger.info(f"Raw to branze processed, filename: {filename}")

        bucket, path = parse_location(filename)
        zt_trees_bronze_to_silver_service = (
            container.zt_trees_bronze_to_silver_service()
        )
        zt_trees_bronze_to_silver_service.set_job_id(self.event.jobId)
        filename = zt_trees_bronze_to_silver_service.handle(
            bucket,
            path,
            event,
            self.event.articleId,
            self.event.orgId,
            self.event.connectorId,
        )
        self._logger.info(f"Bronze to silver processed, filename: {filename}")

        bucket, path = parse_location(filename)
        zt_trees_silver_to_gold_service = (
            container.zt_trees_silver_to_gold_service()
        )
        zt_trees_silver_to_gold_service.set_job_id(self.event.jobId)
        ids = zt_trees_silver_to_gold_service.handle(
            bucket,
            path,
            event,
            self.event.articleId,
            self.event.orgId,
            self.event.connectorId,
        )
        self._logger.info(f"Silver to gold processed, ids {str(ids)}")

    def run_article(self):
        self._logger.info("Article syncying process strated")
        ops = {
            embed_jobs_pb2.ArticleOperation.CREATE: article_kb.BronzeToSilverService.OP_INSERT,  # noqa: E501
            embed_jobs_pb2.ArticleOperation.UPDATE: article_kb.BronzeToSilverService.OP_UPDATE,  # noqa: E501
            embed_jobs_pb2.ArticleOperation.DELETE: article_kb.BronzeToSilverService.OP_DELETE,  # noqa: E501
        }

        article_kb_bronze_to_silver_service = (
            container.article_kb_bronze_to_silver_service()
        )
        article_kb_bronze_to_silver_service.set_job_id(self.event.jobId)
        payload = article_kb_bronze_to_silver_service.handle(
            self.event.location.bucket,
            self.event.location.path,
            self.event.articleId,
            self.event.orgId,
            self.event.connectorId,
            ops[self.event.operation],
        )
        self._logger.info(
            "Bronze to silver processed, payload: " + json.dumps(payload)
        )

        if payload is None:
            return

        article_kb_silver_to_gold_service = (
            container.article_kb_silver_to_gold_service()
        )
        article_kb_silver_to_gold_service.set_job_id(self.event.jobId)
        ids = article_kb_silver_to_gold_service.handle(
            payload["bucket"],
            payload["key"],
            payload["connector_id"],
            payload["detail_type"],
            self.event.articleId,
            self.event.orgId,
        )
        self._logger.info(f"Silver to gold processed, ids {str(ids)}")

    def run(self, event: embed_jobs_pb2.ArticleNotification):
        self.event = event
        started_at = time.time()
        try:
            if self.event.source == "zingtree":
                return self.run_zingtree()

            return self.run_article()
        except NotifiedException as e:
            self._logger.error(
                f"Error handling transformation, exception notified: {e}"
            )
            return
        except Exception as e:
            self._logger.error(f"Error processing event: {e}")
            self._notify_failure(self.event, str(e), started_at)
            return
