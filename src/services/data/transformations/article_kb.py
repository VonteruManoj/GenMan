import os.path
from typing import List

import src.proto.embed_job_status_pb2 as embed_job_status_pb2
from src.contracts.embedder import EmbedderInterface
from src.contracts.events import EventProducerInterface
from src.contracts.storage import StorageInterface
from src.core.deps.logger import with_logger
from src.data.chunkers.chunker import Chunker
from src.data.transformations.article_kb import (
    BronzeToSilverTransformation,
    SilverToGoldTransformation,
)
from src.data.util import S3IsolationLocationParser
from src.exceptions.transformations import NotifiedException
from src.repositories.models.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.services.data.transformations.base import BaseService


@with_logger()
class BronzeToSilverService(BaseService):
    FROM_STAGE: str = "bronze"
    TO_STAGE: str = "silver"

    def __init__(
        self,
        assets_repo: StorageInterface,
        event_producer: EventProducerInterface,
        app_url: str,
        silver_to_gold_enable: bool,
    ) -> None:
        super().__init__(assets_repo, event_producer)
        self._app_url = app_url
        self.silver_to_gold_enable = bool(silver_to_gold_enable)

    def handle(
        self,
        bucket: str,
        path: str,
        article_id: str,
        org_id: int,
        connector_id: int,
        op_type: str,
    ):
        self._set_notifier_data(article_id, org_id, connector_id)
        match op_type:
            case self.OP_INSERT:
                return self._insert(
                    bucket,
                    path,
                    article_id,
                    org_id,
                    connector_id,
                )
            case self.OP_UPDATE:
                return self._update(
                    bucket,
                    path,
                    article_id,
                    org_id,
                    connector_id,
                )
            case self.OP_DELETE:
                return self._delete(
                    bucket,
                    path,
                    article_id,
                    org_id,
                    connector_id,
                )
            case _:
                raise ValueError(f"Invalid operation type: {op_type}")

    def _insert(
        self,
        bucket: str,
        path: str,
        article_id: str,
        org_id: int,
        connector_id: int,
        raise_exception: bool = False,
        notify: bool = True,
    ):
        self._logger.info(
            f'[BronzeToSilver::SalesforceKB] Insert: doc_id: "{article_id}" '
            f'org_id: "{org_id}" bucket: "{bucket}" path: "{path}"'
        )
        key = f"{article_id}.json"
        try:
            if notify:
                self._notify(
                    embed_job_status_pb2.ArticleState.NORMALIZING,
                    embed_job_status_pb2.FailureStatus.SUCCESS,
                )

            filepath = os.path.join(path, key)

            # Output bucket-key
            self.calculate_output_location(bucket, filepath)

            self._logger.info(
                "Transforming salesforce knowledge json file into silver"
            )

            # Retrieve the drive JSON file
            data = self._assets_repo.get_json(filepath, bucket)

            # Handle metadata and content
            data["org_id"] = org_id
            data["connector_id"] = connector_id
            transformer = BronzeToSilverTransformation(data)
            output = transformer.handle()

            # Save the transformed drive json file
            self._logger.info(
                f"Saving the transformed salesforce KB json file in bucket "
                f"{self._output_bucket} and file {self._output_key}"
            )
            self._assets_repo.put_json(
                self._output_key, output, self._output_bucket
            )

            if self.silver_to_gold_enable:
                return {
                    "bucket": self._output_bucket,
                    "key": self._output_key,
                    "detail_type": "Object Created",
                    "connector_id": connector_id,
                }
            return None
        except Exception as e:
            if notify:
                self._notify(
                    embed_job_status_pb2.ArticleState.NORMALIZING_FAILED,
                    embed_job_status_pb2.FailureStatus.FAILED,
                    str(e),
                )
            self._logger.error(f'Bronze to Silver :: Error: "{str(e)}"')

            if raise_exception:
                raise NotifiedException(str(e))

    def _update(
        self,
        bucket: str,
        path: str,
        article_id: str,
        org_id: int,
        connector_id: int,
        notify: bool = True,
    ):
        if notify:
            self._notify(
                embed_job_status_pb2.ArticleState.NORMALIZING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            )

        self._logger.info(
            f'[BronzeToSilver::SalesforceKB] Update: doc_id: "{article_id}" '
            f'org_id: "{org_id}" bucket: "{bucket}" path: "{path}"'
        )

        key = f"{article_id}.json"
        filepath = os.path.join(path, key)

        # Output bucket-key
        self.calculate_output_location(bucket, filepath)

        try:
            self._delete(
                bucket,
                path,
                article_id,
                org_id,
                connector_id,
                raise_exception=True,
                notify=False,
                update=True,
            )
            return self._insert(
                bucket,
                path,
                article_id,
                org_id,
                connector_id,
                raise_exception=True,
                notify=True,
            )

        except Exception as e:
            if notify:
                self._notify(
                    embed_job_status_pb2.ArticleState.NORMALIZING_FAILED,
                    embed_job_status_pb2.FailureStatus.FAILED,
                    str(e),
                )

                raise NotifiedException(str(e))

    def _delete(
        self,
        bucket: str,
        path: str,
        article_id: str,
        org_id: int,
        connector_id: int,
        raise_exception: bool = False,
        notify: bool = True,
        update: bool = False,
    ):
        self._logger.info(
            f'[BronzeToSilver::SalesforceKB] Delete: doc_id: "{article_id}" '
            f'org_id: "{org_id}" bucket: "{bucket}" path: "{path}"'
        )

        try:
            key = f"{article_id}.json"
            filepath = os.path.join(path, key)

            self._logger.info("Deleting files from bucket")

            # Output bucket-key
            self.calculate_output_location(bucket, filepath)

            if not update:
                self._assets_repo.delete_file(filepath, bucket)
                if self.silver_to_gold_enable:
                    self._logger.info(
                        "[REQUESTING] requesting silver-to-gold for "
                        f"{article_id}"
                    )
                    return {
                        "bucket": self._output_bucket,
                        "key": self._output_key,
                        "detail_type": "Object Deleted",
                        "connector_id": connector_id,
                    }
                return None
        except Exception as e:
            if notify:
                self._notify(
                    embed_job_status_pb2.ArticleState.NORMALIZING_FAILED,
                    embed_job_status_pb2.FailureStatus.FAILED,
                    str(e),
                )

            if raise_exception:
                raise NotifiedException(str(e))


@with_logger()
class SilverToGoldService(BaseService):
    FROM_STAGE = "silver"
    TO_STAGE = "gold"

    def __init__(
        self,
        assets_repo: StorageInterface,
        event_producer: EventProducerInterface,
        embedder: EmbedderInterface,
        items_repository: SemanticSearchRepository,
        chunker: Chunker,
    ) -> None:
        super().__init__(assets_repo, event_producer)
        self._embedder = embedder
        self._items_repository = items_repository
        self.chunker = chunker

    def handle(
        self,
        bucket: str,
        key: str,
        connector_id: int,
        event: str,
        article_id: str,
        org_id: int,
    ) -> List[int]:
        self._set_notifier_data(article_id, org_id, connector_id)

        # Delete the records from the database, in any case
        self._logger.info("Removing records from the database")
        parser = S3IsolationLocationParser(key)
        deleted_ids = self._items_repository.remove_item(
            parser.get_id(), int(parser.get_org_id())
        )

        article_id = key.split("/")[-1].split(".")[0]
        if event == "Object Deleted":
            self._logger.info("Object deleted, returning ids.")
            self._assets_repo.delete_file(key, bucket)
            self._notify(
                embed_job_status_pb2.ArticleState.COMPLETE,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            )
            return deleted_ids
        elif event == "Object Created":
            self._logger.info("Creating object in the database.")
            self._notify(
                embed_job_status_pb2.ArticleState.EMBEDDING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            )
            json_data = self._assets_repo.get_json(key, bucket)

            org_id = parser.get_org_id()
            json_data["org_id"] = org_id
            json_data["connector_id"] = connector_id

            inserted_ids = []
            transformer = SilverToGoldTransformation(
                json_data, self._embedder, self.chunker
            )
            records = transformer.handle()

            # If the content is empty skip it
            if len(records) == 0:
                self._logger.info(
                    "[Semantic-Search] Salesforce content, and title are empty"
                    ", skipping (document_id): (%s)",
                    json_data["document_id"],
                )
                self._notify(
                    embed_job_status_pb2.ArticleState.COMPLETE,
                    embed_job_status_pb2.FailureStatus.SUCCESS,
                )
                return inserted_ids

            document_item = self._items_repository.find_document(
                json_data["document_id"],
                json_data["connector_id"],
                json_data["org_id"],
            )
            if not document_item:
                document_item = self._items_repository.create_document(
                    records[0]["org_id"],
                    records[0]["language"],
                    records[0]["title"],
                    records[0]["description"],
                    records[0]["tags"],
                    records[0]["data"],
                    records[0]["connector_id"],
                    records[0]["document_id"],
                    records[0]["created_at"],
                    records[0]["updated_at"],
                )

            for record in records:
                inserted = self._items_repository.create_item(
                    record["embeddings"],
                    record["chunk"],
                    record["snippet"],
                    document_item,
                )
                inserted_ids.append(inserted.id)

            self._notify(
                embed_job_status_pb2.ArticleState.COMPLETE,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            )

            return inserted_ids
