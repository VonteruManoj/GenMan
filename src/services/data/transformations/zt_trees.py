import json

import src.proto.embed_job_status_pb2 as embed_job_status_pb2
from src.contracts.embedder import EmbedderInterface
from src.contracts.events import EventProducerInterface
from src.contracts.storage import StorageInterface
from src.core.deps.logger import with_logger
from src.data.chunkers.chunker import Chunker
from src.data.transformations.zt_trees import (
    BronzeToSilverTransformation,
    RawToBronzeTransformation,
    SilverToGoldTransformation,
)
from src.data.util import S3ZTTreesIsolationLocationParser
from src.exceptions.transformations import NotifiedException
from src.repositories.models.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.repositories.services.connectors_svc import ConnectorsSvcRepository
from src.services.data.transformations.base import BaseService


class RawToBronzeService(BaseService):
    FROM_STAGE: str = "raw"
    TO_STAGE: str = "bronze"

    def __init__(
        self,
        assets_repo: StorageInterface,
        event_producer: EventProducerInterface,
    ) -> None:
        super().__init__(assets_repo, event_producer)

    def handle(
        self,
        bucket: str,
        key: str,
        event: str,
        article_id: str,
        org_id: int,
        connector_id: int,
    ) -> str:
        try:
            self._set_notifier_data(article_id, org_id, connector_id)

            self._notify(
                embed_job_status_pb2.ArticleState.NORMALIZING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            )

            # Output bucket-key
            self.calculate_output_location(bucket, key)

            # Delete the output file if the event is "Object Deleted"
            if event == "Object Deleted":
                self._assets_repo.delete_file(
                    self._output_key, self._output_bucket
                )
                return self.full_output_location()

            # Retrieve the tree JSON file
            tree_json = self._assets_repo.get_json(key, bucket)

            tree_json = json.loads(tree_json["details"][0]["value"])

            # Transform the tree
            transformer = RawToBronzeTransformation(tree_json)
            transformed_tree = transformer.handle()

            # Save the transformed tree
            self._assets_repo.put_json(
                self._output_key, transformed_tree, self._output_bucket
            )

            return self.full_output_location()
        except Exception as e:
            self._notify(
                embed_job_status_pb2.ArticleState.NORMALIZING_FAILED,
                embed_job_status_pb2.FailureStatus.FAILED,
                str(e),
            )
            raise NotifiedException(str(e))


class BronzeToSilverService(BaseService):
    FROM_STAGE: str = "bronze"
    TO_STAGE: str = "silver"

    def __init__(
        self,
        assets_repo: StorageInterface,
        event_producer: EventProducerInterface,
    ) -> None:
        super().__init__(assets_repo, event_producer)

    def handle(
        self,
        bucket: str,
        key: str,
        event: str,
        article_id: str,
        org_id: int,
        connector_id: int,
    ):
        self._set_notifier_data(article_id, org_id, connector_id)
        try:
            # Output bucket-key
            self.calculate_output_location(bucket, key)

            # Delete the output file if the event is "Object Deleted"
            if event == "Object Deleted":
                self._assets_repo.delete_file(
                    self._output_key, self._output_bucket
                )
                return self.full_output_location()

            # Retrieve the tree JSON file
            json_data = self._assets_repo.get_json(key, bucket)

            # Output
            output = dict()

            # Handle meta
            transformer = BronzeToSilverTransformation(json_data["meta"])
            output["meta"] = transformer.handle()["metadata"]
            # raise Exception(json_data["nodes"])
            # Handle nodes
            output["nodes"] = dict()
            for node_id in json_data["nodes"]:
                transformer = BronzeToSilverTransformation(
                    json_data["nodes"][node_id]
                )
                transformed = transformer.handle()
                output["nodes"][node_id] = dict()
                output["nodes"][node_id]["content"] = transformed["content"]
                output["nodes"][node_id]["meta"] = transformed["metadata"]

            # Save the transformed tree
            self._assets_repo.put_json(
                self._output_key, output, self._output_bucket
            )

            return self.full_output_location()
        except Exception as e:
            self._notify(
                embed_job_status_pb2.ArticleState.NORMALIZING_FAILED,
                embed_job_status_pb2.FailureStatus.FAILED,
                str(e),
            )
            raise NotifiedException(str(e))


@with_logger()
class SilverToGoldService(BaseService):
    FROM_STAGE: str = "silver"
    TO_STAGE: str = "gold"

    def __init__(
        self,
        assets_repo: StorageInterface,
        event_producer: EventProducerInterface,
        embedder: EmbedderInterface,
        items_repository: SemanticSearchRepository,
        chunker: Chunker,
        connectors_service: ConnectorsSvcRepository,
    ) -> None:
        super().__init__(assets_repo, event_producer)
        self.concat = None
        self._embedder = embedder
        self._items_repository = items_repository
        self._chunker = chunker
        self.connectors_service = connectors_service

    def handle(
        self,
        bucket: str,
        key: str,
        event: str,
        article_id: str,
        org_id: int,
        connector_id: int,
    ):
        self._set_notifier_data(article_id, org_id, connector_id)
        try:
            self._notify(
                embed_job_status_pb2.ArticleState.EMBEDDING,
                embed_job_status_pb2.FailureStatus.SUCCESS,
            )
            # Delete the records from the database, in any case
            self._logger.info("Removing records from the database")
            parser = S3ZTTreesIsolationLocationParser(key)
            deleted_ids = self._items_repository.remove_items_like(
                f"{parser.get_id()}::%", int(parser.get_org_id())
            )

            if event == "Object Deleted":
                self._logger.info("Object deleted, returning ids.")
                self._notify(
                    embed_job_status_pb2.ArticleState.COMPLETE,
                    embed_job_status_pb2.FailureStatus.SUCCESS,
                )

                return deleted_ids
            elif event == "Object Created":
                # Retrieve the tree JSON file
                self._logger.info("Creating object in the database.")
                json_data = self._assets_repo.get_json(key, bucket)
                tree_meta_data = json_data["meta"]
                tree_meta_data["tree_id"] = tree_meta_data.pop("id")
                tree_meta_data["tree_name"] = tree_meta_data.pop("name")
                tree_meta_data["tree_description"] = tree_meta_data.pop(
                    "description"
                )

                try:
                    connector_type = list(
                        filter(
                            lambda x: x.provider == "zingtree",
                            self.connectors_service.get_connector_types(
                                tree_meta_data["org_id"]
                            ),
                        )
                    )[0]
                    connector_id = (
                        self.connectors_service.get_connectors_by_connector_type_id(  # noqa: E501
                            tree_meta_data["org_id"], connector_type.id
                        )
                    )[0].id
                    tree_meta_data["connector_id"] = connector_id
                except Exception:
                    raise ValueError(
                        "Connector or ConnectorType not configured for "
                        "organization"
                    )

                # Handle nodes
                inserted_ids = []
                for node_id in json_data["nodes"]:
                    json_data["nodes"][node_id]["meta"]["node_id"] = node_id
                    transformer = SilverToGoldTransformation(
                        json_data["nodes"][node_id]["content"],
                        json_data["nodes"][node_id]["meta"],
                        tree_meta_data,
                        self._embedder,
                        self._chunker,
                    )
                    records = transformer.handle()

                    # If the node content is empty skip it
                    if len(records) == 0:
                        self._logger.info(
                            "[Semantic-Search] Node content,"
                            " question, and page_title are empty,"
                            " skipping (project_id, "
                            "project_node_id): (%s, %s)",
                            tree_meta_data["tree_id"],
                            node_id,
                        )
                        continue

                    document_item = self._items_repository.find_document(
                        records[0]["document_id"],
                        records[0]["connector_id"],
                        records[0]["org_id"],
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
                        # Initially a list with a single dictionary per node
                        inserted = self._items_repository.create_item(
                            record["embeddings"],
                            record["chunk"],
                            record["snippet"],
                            document_item,
                        )
                        inserted_ids.append(inserted.id)

                # At this stage we do not need to
                # save the transformed tree, only
                # to save the records in the database and return True

                self._notify(
                    embed_job_status_pb2.ArticleState.COMPLETE,
                    embed_job_status_pb2.FailureStatus.SUCCESS,
                )
                return inserted_ids
        except Exception as e:
            self._notify(
                embed_job_status_pb2.ArticleState.EMBEDDING_FAILED,
                embed_job_status_pb2.FailureStatus.FAILED,
            )
            raise NotifiedException(str(e))
