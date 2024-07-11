from typing import Dict, List, Union

import src.repositories.models.analytics.semantic_search_analytics_repository as ssar  # noqa: E501
from src.api.v1.endpoints.requests.semantic_search import (
    SearchFilters,
    TagsWithMetaFields,
)
from src.api.v1.endpoints.responses.semantic_search import TagMeta
from src.builders.queries.semantic_search import WidgetFiltersBuilder
from src.contracts.embedder import EmbedderInterface
from src.contracts.summarizer import SummarizerInterface
from src.core.deps.logger import with_logger
from src.exceptions.http import NotFoundException
from src.models.semantic_search_item import SemanticSearchItem
from src.repositories.audit import AuditInMemoryRepository
from src.repositories.models.semantic_search_repository import (
    SemanticSearchRepository,
)
from src.repositories.services.config_svc import ConfigSvcRepository
from src.repositories.services.connectors_svc import ConnectorsSvcRepository
from src.repositories.services.lime import LimeRepository
from src.schemas.services.connectors_svc import Connector
from src.util.tags_parser import TagParser


@with_logger()
class SemanticSearchService:
    def __init__(
        self,
        embedder: EmbedderInterface,
        items_repository: SemanticSearchRepository,
        semantic_search_analytics_repository: ssar.SemanticSearchAnalyticsRepository,  # noqa: E501
        connectors_svc_repository: ConnectorsSvcRepository,
        config_svc_repository: ConfigSvcRepository,
        lime_repository: LimeRepository,
        audit_repository: AuditInMemoryRepository,
    ) -> None:
        self._embedder = embedder
        self._items_repository = items_repository
        self._semantic_search_analytics_repository = (
            semantic_search_analytics_repository
        )
        self._connectors_svc_repository = connectors_svc_repository
        self._config_svc_repository = config_svc_repository
        self._lime_repository = lime_repository
        self._audit_repository = audit_repository

    def search(
        self,
        search: str,
        org_id: int,
        deployment_id: str,
        filters: SearchFilters,
        limit: int | None,
        sort_by: str = "relevance",
    ) -> (Dict[str, str | List[SemanticSearchItem]], bool):
        """
        Handle semantic search request.

        Parameters
        ----------
        text : str
            Text to be searched.
        org_id: int
            Organization ID.
        limit : int
            Number of results to return.
        sort_by : str
            Sort by relevance or alphabetical.

        Returns
        -------
        (List[SemanticSearchItem], bool)
            List of semantic search items. And errors flag.
        """
        widget = (
            self._config_svc_repository.get_search_widget_by_deployment_id(
                org_id, deployment_id
            )
        )
        if not widget:
            raise NotFoundException(
                message=f"Widget {deployment_id} not found"
            )

        connectors = self._connectors_svc_repository.get_all_connectors(org_id)
        filters = WidgetFiltersBuilder(widget, connectors).build_from(filters)

        if self._audit_repository.is_agent():
            user_tags = self._lime_repository.get_agent_tags(
                self._audit_repository.data.causer_id
            )
            if len(user_tags) > 0:
                filters.zt_tags = user_tags

        embeddings = self._embedder.embed(search)[0]
        options, distances = self._items_repository.search(
            embeddings, org_id, filters, limit
        )

        # Analytics
        # NOTE: results should be saved in as fetched (relevant sort)
        # if they're re-sorted alphabetically, the actual order clicked
        # by the user will be recorded in the clicks' analytics.
        batch = self._semantic_search_analytics_repository.from_search(
            search=search,
            filters=filters.dict(),
            limit=limit,
            sort_by=sort_by,
            options=options,
            distances=distances,
            deployment_id=deployment_id,
        )

        # if there are no options, return empty list
        if not options:
            return (
                {
                    "analytics_id": str(batch.id),
                    "answer": "There's no items to answer this question.",
                    "options": [],
                },
                False,
            )

        # handle sort
        if sort_by == "alphabetical":
            sorted_options = list(
                sorted(
                    options[1:],
                    key=lambda x: x.document.sorting_values(),
                )
            )
            options = [options[0]] + sorted_options

        # map to dict
        output = []
        for index, option in enumerate(options):
            try:
                item = option.to_dict()
                item["distance"] = distances[index]
                output.append(item)
            except Exception:
                self._logger.error(
                    "[Semantic-Search] Failed to map option to dict"
                )
                continue

        return (
            {
                "analytics_id": str(batch.id),
                "options": output,
            },
            len(options) != len(output),
        )

    def get_search_suggestions(
        self,
        search: str,
        org_id: int,
        deployment_id: str,
        filters: SearchFilters,
        limit: int | None,
    ) -> list[str]:
        widget = (
            self._config_svc_repository.get_search_widget_by_deployment_id(
                org_id, deployment_id
            )
        )
        if not widget:
            raise NotFoundException(
                message=f"Widget {deployment_id} not found"
            )

        connectors = self._connectors_svc_repository.get_all_connectors(org_id)
        filters = WidgetFiltersBuilder(widget, connectors).build_from(filters)

        if self._audit_repository.is_agent():
            user_tags = self._lime_repository.get_agent_tags(
                self._audit_repository.data.causer_id
            )
            if len(user_tags) > 0:
                filters.zt_tags = user_tags

        return self._items_repository.get_search_suggestions(
            search=search,
            org_id=org_id,
            filters=filters,
            limit=limit,
        )

    def get_tags(
        self, org_id: int, with_meta: list[TagsWithMetaFields] = []
    ) -> Union[dict[str, list[str]], list[dict] | None]:
        if TagsWithMetaFields.connectorsCount in with_meta:
            data = self._items_repository.get_tags_with_meta(org_id)
            meta = []
            for d in [
                (TagParser.from_str([r[0]]).tags, r[1], r[2]) for r in data
            ]:
                tag = list(d[0].keys())[0]
                meta.append(
                    TagMeta(
                        tag=tag,
                        value=d[0][tag][0],
                        connectorId=d[1],
                        count=d[2],
                    )
                )
            tags = TagParser.from_str([m[0] for m in data]).tags

            return tags, {"connectorsCount": meta}
        else:
            return (
                TagParser.from_str(
                    self._items_repository.get_tags(org_id)
                ).tags,
                None,
            )

    def get_connectors(
        self,
        org_id: int,
    ) -> list[Connector]:
        return self._connectors_svc_repository.get_all_connectors(
            org_id=org_id
        )

    def get_deployment_connectors(
        self, org_id: int, deployment_id: str
    ) -> list[Connector]:
        widget = (
            self._config_svc_repository.get_search_widget_by_deployment_id(
                org_id, deployment_id
            )
        )
        if not widget:
            raise NotFoundException(
                message=f"Widget {deployment_id} not found"
            )

        connectors = self.get_connectors(org_id)
        cs = []
        if widget.enableExternalSources:
            cs = [
                connector
                for connector in connectors
                if connector.id
                in widget.metadataInfo.sourcesConfig.externalSource.connectorIds  # noqa: E501
            ]

        if widget.enableDecisionTrees:
            zt_connector = next(
                filter(
                    lambda c: c.connector_type.provider == "zingtree",
                    connectors,
                )
            )
            if zt_connector:
                cs.append(zt_connector)

        return cs

    def get_documents(
        self,
        org_id: int | None,
        connector_id: int | None,
        limit: int | None,
        offset: int | None,
    ) -> list[dict]:
        documents = self._items_repository.get_documents(
            org_id=org_id,
            connector_id=connector_id,
            limit=limit,
            offset=offset,
        )
        return [document.to_dict() for document in documents]

    def get_languages(
        self,
        org_id: int,
    ) -> list[str]:
        return self._items_repository.get_languages(org_id=org_id)

    def deployment_has_documents(
        self,
        deployment_id: str,
    ) -> bool:
        org_id = self._audit_repository.data.org_id

        try:
            widget = (
                self._config_svc_repository.get_search_widget_by_deployment_id(
                    org_id, deployment_id
                )
            )
        except Exception:
            widget = None

        if not widget:
            raise NotFoundException(
                message=f"Widget {deployment_id} not found for org {org_id}"
            )

        connectors = self._connectors_svc_repository.get_all_connectors(org_id)
        filters = WidgetFiltersBuilder(widget, connectors).build_from(
            SearchFilters()
        )

        return self._items_repository.deployment_has_documents(org_id, filters)


@with_logger()
class SummarizeAnswerService:
    def __init__(
        self,
        embedder: EmbedderInterface,
        summarizer: SummarizerInterface,
        items_repository: SemanticSearchRepository,
        app_env: str,
        connectors_svc_repository: ConnectorsSvcRepository,
        config_svc_repository: ConfigSvcRepository,
    ) -> None:
        self._embedder = embedder
        self._summarizer = summarizer
        self._items_repository = items_repository
        self._app_env = app_env
        self._connectors_svc_repository = connectors_svc_repository
        self._config_svc_repository = config_svc_repository

    def handle(
        self,
        query: str,
        org_id: int,
        deployment_id: str,
        options_id_list: list[int] | None = None,
    ) -> Dict[str, str | List[SemanticSearchItem]]:
        """
        Summarize semantic search results.

        Parameters
        ----------
        query : str
            Query to search for.
        org_id: int
            Organization ID.
        options_id_list : [int]
            List of SemanticSearchItem's IDs to summarize.

        Returns
        -------
        str
            Summarized answer from given SemanticSearchItem's IDs.
        """

        widget = (
            self._config_svc_repository.get_search_widget_by_deployment_id(
                org_id, deployment_id
            )
        )
        if not widget:
            raise NotFoundException(
                message=f"Widget {deployment_id} not found"
            )

        connectors = self._connectors_svc_repository.get_all_connectors(org_id)
        filters = WidgetFiltersBuilder(widget, connectors).build_from(
            SearchFilters()
        )

        if self._app_env == "local":
            embeddings = self._embedder.embed(query)[0]
            options = self._items_repository.search_best(
                embeddings,
                org_id,
                filters=filters,
            )
            return dict(
                answer="Lorem ipsum dolor sit amet, consectetur"
                " adipiscing elit. Integer ut elit id leo imperdiet"
                " placerat. Nam ligula odio, auctor eu velit quis,"
                " tincidunt fringilla quam. Etiam fermentum ligula"
                " vel dolor ultricies, a viverra nulla aliquet."
                " Duis elit mi, ornare vel pulvinar ac, cursus"
                " vitae elit. Ut auctor lacinia tempor. Nulla"
                " fermentum libero id neque ullamcorper, eget"
                " ornare tellus bibendum. Duis suscipit eleifend"
                " elementum. Pellentesque arcu est, mattis vitae"
                " elit eu, dapibus sollicitudin ante. Nunc"
                " molestie lobortis magna, eu mattis"
                " libero mollis auctor.",
                options=[o.to_dict() for o in options],
            )

        if options_id_list:
            options = self._items_repository.find_semantic_search_items_by_ids(
                options_id_list, org_id
            )
        else:
            embeddings = self._embedder.embed(query)[0]
            options = self._items_repository.search_best(
                embeddings,
                org_id,
                filters=filters,
            )
        # If still there are no options, log and return error message
        if not options:
            self._logger.error(
                "[Summarize-Answer] There is no context to answer this "
                "question."
            )
            return {
                "answer": "There is no context to answer this question.",
                "options": [],
            }

        answer = self._summarizer.summarize(
            [option.snippet for option in options], query
        )
        return {"answer": answer, "options": [o.to_dict() for o in options]}
