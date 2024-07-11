import json
from copy import deepcopy

from sqlalchemy import ARRAY, String, select, text, union_all
from sqlalchemy.sql import and_, not_, or_
from sqlalchemy.sql.expression import func

from src.api.v1.endpoints.requests.semantic_search import SearchFilters
from src.core.deps.logger import with_logger
from src.exceptions.http import NotFoundException
from src.models.semantic_search_item import (
    SemanticSearchDocument,
    SemanticSearchItem,
)
from src.schemas.services.config_svc import SearchWidget
from src.schemas.services.connectors_svc import Connector
from src.util.tags_parser import TagParser


@with_logger()
class SemanticSearchBaseQueryBuilder:
    def __init__(self, org_id: int):
        self.org_id = org_id
        self.limit = None
        self.filters = SearchFilters()
        self._query = None

    def _prepare_data_filter(self, filter_data: dict):
        filters = []
        self._logger.info(f"Query filter_data: {json.dumps(filter_data)}")
        for key, value in filter_data.items():
            if isinstance(value, str):
                filters.append(
                    SemanticSearchDocument.data[key].cast(String)
                    == f'"{value}"'
                )
            elif isinstance(value, int):
                filters.append(
                    SemanticSearchDocument.data[key].cast(String) == str(value)
                )
            elif isinstance(value, list):
                if len(value) < 1:
                    filters.append(
                        SemanticSearchDocument.data[key].cast(String).in_([])
                    )
                    continue

                mValue = []
                if isinstance(value[0], str):
                    mValue = [f'"{v}"' for v in value]
                elif isinstance(value[0], int):
                    mValue = [str(v) for v in value]
                else:
                    details = json.dumps({"key": key, "value": value})
                    self._logger.warning(
                        f"Search filter not supported: {details}"
                    )
                    continue

                filters.append(
                    SemanticSearchDocument.data[key].cast(String).in_(mValue)
                )
            else:
                details = json.dumps({"key": key, "value": value})
                self._logger.warning(
                    f"Search filter not supported: {details}",
                )
                continue

        return filters

    def _apply_filters(self):
        if self.filters.tags:
            flattened_tags = TagParser.from_dict(self.filters.tags).to_str()
            self._query = self._query.filter(
                func.cast(SemanticSearchDocument.tags, ARRAY(String)).op("&&")(
                    flattened_tags
                )
            )

        self._logger.info(f"Query connectors: {self.filters.connectors}")
        self._query = self._query.filter(
            SemanticSearchDocument.connector_id.in_(self.filters.connectors)
        )

        self._logger.info(
            "ZT trees constrain: "
            f"{self.filters.zt_connector_id}::{self.filters.zt_tree_ids}"
        )
        if self.filters.zt_connector_id and self.filters.zt_tree_ids:
            # sem-ser uses live ids
            zt_tree_ids = [f'"{v*1000}"' for v in self.filters.zt_tree_ids]
            self._query = self._query.filter(
                or_(
                    SemanticSearchDocument.connector_id
                    != self.filters.zt_connector_id,
                    and_(
                        SemanticSearchDocument.connector_id
                        == self.filters.zt_connector_id,
                        SemanticSearchDocument.data["tree_id"]
                        .cast(String)
                        .in_(zt_tree_ids),
                    ),
                )
            )

        if self.filters.zt_connector_id and self.filters.zt_tags:
            flattened_tags = TagParser.from_dict(
                {"zt_trees_trees": self.filters.zt_tags}
            ).to_str()
            self._query = self._query.filter(
                or_(
                    SemanticSearchDocument.connector_id
                    != self.filters.zt_connector_id,
                    and_(
                        SemanticSearchDocument.connector_id
                        == self.filters.zt_connector_id,
                        func.cast(
                            SemanticSearchDocument.tags, ARRAY(String)
                        ).op("&&")(flattened_tags),
                    ),
                )
            )

        if self.filters.data:
            filters = self._prepare_data_filter(self.filters.data)
            self._query = self._query.filter(and_(*filters))

        if self.filters.languages:
            language_patterns = [
                f"{language}%" for language in self.filters.languages
            ]
            self._query = self._query.filter(
                text(
                    f"{SemanticSearchDocument.__tablename__}.language"
                    " LIKE ANY(:language_patterns)"
                ).bindparams(language_patterns=language_patterns)
            )

        if self.filters.contentScopeFilter:
            scope_filters = []
            hide_all = []

            for source in self.filters.contentScopeFilter.sources:
                if source.action == "show":
                    if len(source.tags) == 0:
                        # if no tags are provided, show nothing
                        hide_all.append(
                            and_(
                                SemanticSearchDocument.connector_id
                                != source.connectorId,
                            )
                        )
                    else:
                        flattened_tags = TagParser.from_str(
                            source.tags
                        ).to_str()

                        scope_filters.append(
                            and_(
                                SemanticSearchDocument.connector_id
                                == source.connectorId,
                                and_(
                                    func.cast(
                                        SemanticSearchDocument.tags,
                                        ARRAY(String),
                                    ).op("&&")(flattened_tags)
                                ).self_group(),
                            ).self_group()
                        )

                # if source.action == "hide" and len(source.tags) != 0:
                if source.action == "hide":
                    if len(source.tags) == 0:
                        # if no tags are provided, show everything
                        scope_filters.append(
                            and_(
                                SemanticSearchDocument.connector_id
                                == source.connectorId,
                            )
                        )
                    else:
                        flattened_tags = TagParser.from_str(
                            source.tags
                        ).to_str()

                        scope_filters.append(
                            and_(
                                SemanticSearchDocument.connector_id
                                == source.connectorId,
                                and_(
                                    not_(
                                        func.cast(
                                            SemanticSearchDocument.tags,
                                            ARRAY(String),
                                        ).op("&&")(flattened_tags)
                                    )
                                ).self_group(),
                            )
                        )
            self._query = self._query.filter(or_(*scope_filters).self_group())
            self._query = self._query.filter(and_(*hide_all).self_group())

    def _apply_limit(self):
        if self.limit:
            self._query = self._query.limit(self.limit)


class SemanticSearchSearchQueryBuilder(SemanticSearchBaseQueryBuilder):
    def __init__(self, embeddings: list[float], org_id: int, treshold: float):
        super().__init__(org_id)
        self.embeddings = embeddings
        self.treshold = treshold

    def _start_query(self):
        self._query = (
            select(SemanticSearchItem.id)
            .distinct(
                SemanticSearchItem.document_id,
            )
            .join(SemanticSearchDocument)
            .where(SemanticSearchDocument.org_id == self.org_id)
            .order_by(
                SemanticSearchItem.document_id,
                SemanticSearchItem.embeddings.cosine_distance(self.embeddings),
            )
        )

    def build(self) -> select:
        self._start_query()
        self._apply_filters()

        q = (
            select(SemanticSearchItem)
            .add_columns(
                SemanticSearchItem.embeddings.cosine_distance(
                    self.embeddings
                ).label("distance")
            )
            .order_by(text("distance"))
            .where(SemanticSearchItem.id.in_(self._query))
            .filter(
                SemanticSearchItem.embeddings.cosine_distance(self.embeddings)
                < self.treshold * 2
            )
            .limit(self.limit)
        )

        self._logger.info(f"Query: {q}")
        return q

    def _start_best_query(self) -> None:
        self._query = (
            select(SemanticSearchItem)
            .join(SemanticSearchDocument)
            .filter(SemanticSearchDocument.org_id == self.org_id)
            .order_by(
                SemanticSearchItem.embeddings.cosine_distance(self.embeddings),
            )
        )

    def build_best(self) -> select:
        self._start_best_query()
        self._apply_filters()
        self._apply_limit()

        return self._query


class SemanticSearchSearchSuggestionsQueryBuilder(
    SemanticSearchBaseQueryBuilder
):
    def _create_partial_query(self, search: str, column):
        self._query = (
            select(
                column.label("suggestion"),
                func.length(column).label("len"),
            )
            .filter(SemanticSearchDocument.org_id == self.org_id)
            .filter(column.ilike(f"%{search}%"))
            .distinct()
            .order_by("len")
        )

        self._apply_filters()
        self._apply_limit()

    def build(self, search: str) -> select:
        queries = []
        self._create_partial_query(search, SemanticSearchDocument.title)
        queries.append(self._query)
        self._create_partial_query(search, SemanticSearchDocument.description)
        queries.append(self._query)

        union_query = union_all(*queries)

        return (
            select(union_query.c.suggestion, union_query.c.len)
            .distinct()
            .order_by(union_query.c.len)
            .limit(self.limit)
        )


class WidgetFiltersBuilder:
    def __init__(self, widget: SearchWidget, connetors: list[Connector]):
        self._widget = widget
        self._connectors = connetors
        self._filters = SearchFilters()
        self._connector_ids = [c.id for c in self._connectors]

    def build_from(self, filters: SearchFilters) -> SearchFilters:
        self._filters = deepcopy(filters)

        self._merge_conns()
        self._set_zt_conn()
        self._set_content_scopes()

        return self._filters

    def _set_content_scopes(self):
        if self._filters.contentScopeParameters is not None:
            self._filters.contentScopeFilter = {}
            current_scope_index = None
            for scope_parameter in self._filters.contentScopeParameters:
                matching_scope = next(
                    (
                        scope
                        for scope in self._widget.metadataInfo.contentScopes
                        if (
                            scope.parameter.name == scope_parameter["name"]
                            and scope.parameter.value
                            == scope_parameter["value"]
                        )
                    ),
                    None,
                )
                matching_scope_index = (
                    self._widget.metadataInfo.contentScopes.index(
                        matching_scope
                    )
                    if matching_scope
                    else None
                )
                if matching_scope and (
                    current_scope_index is None
                    or matching_scope_index < current_scope_index
                ):
                    self._filters.contentScopeFilter = matching_scope
                    current_scope_index = matching_scope_index

        return

    def _set_zt_conn(self):
        self._filters.zt_connector_id = None
        self._filters.zt_tree_ids = None

        if not self._widget.enableDecisionTrees:
            return

        zt_connector = self._get_zt_connector()
        if not zt_connector:
            return

        self._filters.zt_connector_id = zt_connector.id

        if self._widget.metadataInfo.sourcesConfig.decisionTree.all:
            return

        self._filters.zt_tree_ids = (
            self._widget.metadataInfo.sourcesConfig.decisionTree.treeIds
        )

    def _get_zt_connector(self) -> Connector:
        try:
            return next(
                filter(
                    lambda c: c.connector_type.provider == "zingtree",
                    self._connectors,
                )
            )
        except Exception:
            raise NotFoundException(message="Zingtree connector not found")

    def _merge_conns(self):
        widget_cids = self._conn_ids()
        if not self._filters.connectors and self._filters.connectors != []:
            self._filters.connectors = widget_cids
        else:
            user_cids = self._filters.connectors
            self._filters.connectors = list(set(widget_cids) & set(user_cids))

    def _conn_ids(self) -> list[int]:
        cids = []

        if self._widget.enableDecisionTrees:
            zt_connector = self._get_zt_connector()
            if zt_connector:
                cids.append(zt_connector.id)

        if self._widget.enableExternalSources:
            cids.extend(
                self._widget.metadataInfo.sourcesConfig.externalSource.connectorIds  # noqa: E501
            )

        return list(filter(lambda cid: cid in self._connector_ids, cids))


class SemanticSearchDeployDocumentsCountBuilder(
    SemanticSearchBaseQueryBuilder
):
    def _start_query(self):
        self._query = (
            select(SemanticSearchDocument.id)
            .where(SemanticSearchDocument.org_id == self.org_id)
            .limit(1)
        )

    def build(self) -> select:
        self._start_query()
        self._apply_filters()

        return self._query
