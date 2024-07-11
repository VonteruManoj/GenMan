from typing import List

from src.contracts.embedder import EmbedderInterface
from src.contracts.storage import StorageInterface
from src.core.deps.logger import with_logger
from src.data.chunkers.chunker import Chunker
from src.data.transformations.html import SilverToGoldTransformation
from src.data.util import S3IsolationLocationParser
from src.repositories.models.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.repositories.services.connectors_svc import ConnectorsSvcRepository
from src.services.data.transformations.base import BaseService


@with_logger()
class SilverToGoldService(BaseService):
    FROM_STAGE = "silver"
    TO_STAGE = "gold"

    def __init__(
        self,
        assets_repo: StorageInterface,
        embedder: EmbedderInterface,
        items_repository: SemanticSearchRepository,
        chunker: Chunker,
        connectors_service: ConnectorsSvcRepository,
    ) -> None:
        super().__init__(assets_repo)
        self._embedder = embedder
        self._items_repository = items_repository
        self.chunker = chunker
        self.connectors_service = connectors_service

    def handle(self, bucket: str, key: str, event: str) -> List[int]:
        # Delete the records from the database, in any case
        self._logger.info("Removing records from the database")
        parser = S3IsolationLocationParser(key)
        deleted_ids = self._items_repository.remove_item(
            parser.get_id(), int(parser.get_org_id())
        )

        if event == "Object Deleted":
            self._logger.info("Object deleted, returning ids.")
            return deleted_ids
        elif event == "Object Created":
            self._logger.info("Creating object in the database.")
            json_data = self._assets_repo.get_json(key, bucket)
            json_data["org_id"] = parser.get_org_id()

            try:
                connector_type = list(
                    filter(
                        lambda x: x.provider == "html",
                        self.connectors_service.get_connector_types(
                            json_data["org_id"]
                        ),
                    )
                )[0]
                connector_id = (
                    self.connectors_service.get_connectors_by_connector_type_id(  # noqa: E501
                        json_data["org_id"], connector_type.id
                    )
                )[0].id
                json_data["connector_id"] = connector_id
            except Exception:
                raise ValueError(
                    "Connector or ConnectorType not configured for "
                    "organization"
                )

            inserted_ids = []
            transformer = SilverToGoldTransformation(
                json_data,
                self._embedder,
                self.chunker,
            )
            records = transformer.handle()

            # If the node content is empty skip it
            if len(records) == 0:
                self._logger.info(
                    "[Semantic-Search] HTML content, and title are empty, "
                    "skipping (html_id): (%s)",
                    json_data["html_id"],
                )
                return inserted_ids

            document_item = self._items_repository.find_document(
                json_data["html_id"],
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
                # Initially a list with a single dictionary per node
                inserted = self._items_repository.create_item(
                    record["embeddings"],
                    record["chunk"],
                    record["snippet"],
                    document_item,
                )
                inserted_ids.append(inserted.id)

            return inserted_ids
