import json
import time

import src.proto.embed_job_status_pb2 as embed_job_status_pb2
from src.contracts.events import EventProducerInterface
from src.contracts.storage import StorageInterface
from src.core.config import get_settings
from src.core.deps.logger import with_logger
from src.data.util import S3IsolationLocationSolver


@with_logger()
class BaseService:
    FROM_STAGE: str
    TO_STAGE: str

    OP_INSERT: str = "insert"
    OP_UPDATE: str = "update"
    OP_DELETE: str = "delete"

    def __init__(
        self,
        assets_repo: StorageInterface,
        event_producer: EventProducerInterface = None,
    ) -> None:
        self._assets_repo = assets_repo
        self._event_producer = event_producer
        self._output_bucket = None
        self._output_key = None
        self._job_id = None

    def calculate_output_location(self, bucket: str, key: str):
        s3IsolationLocationSolver = S3IsolationLocationSolver(
            self.FROM_STAGE, self.TO_STAGE
        )
        self._output_bucket = s3IsolationLocationSolver.calculate_bucket(
            bucket
        )
        self._output_key = s3IsolationLocationSolver.calculate_key(key)

    def full_output_location(self) -> str:
        if self._output_bucket is None or self._output_key is None:
            raise Exception(
                "Output bucket and key must be"
                " calculated before calling this method"
            )
        return f"s3://{self._output_bucket}/{self._output_key}"

    def set_job_id(
        self,
        job_id: str,
    ):
        self._job_id = job_id

    def _set_notifier_data(
        self,
        doc_id: str,
        org_id: int,
        connector_id: int,
    ):
        self._notifier_data = {
            "start": time.time(),
            "doc_id": str(doc_id),
            "org_id": int(org_id),
            "connector_id": int(connector_id),
        }

    def _notify(
        self,
        state: int,
        status: int,
        reason: str = "",
    ):
        if self._event_producer is None:
            self._logger.error(
                "No event producer configured, "
                "skipping notification for job status"
            )
            return

        now = time.time()
        dur = int((self._notifier_data["start"] - now) * 1000)
        self._notifier_data["start"] = now

        s = embed_job_status_pb2.NotificationResponse()
        s.id = self._notifier_data["doc_id"]
        s.orgId = self._notifier_data["org_id"]
        s.connectorId = self._notifier_data["connector_id"]
        s.dur = dur
        s.state = int(state)
        s.status = int(status)
        s.reason = str(reason)
        s.jobId = self._job_id

        self._event_producer.produce(
            get_settings().KAFKA_EMBED_JOB_STATUS_TOPIC,
            s.SerializeToString(),
            key=self._job_id,
        )
        self._logger.info(
            f"Notifying new job status: " f"{json.dumps(str(s))}"
        )
