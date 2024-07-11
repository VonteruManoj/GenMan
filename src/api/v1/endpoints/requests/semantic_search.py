from enum import Enum

from fastapi import Header, HTTPException, Query
from pydantic import BaseModel, Field, Json

from src.schemas.services.config_svc import SearchWidgetContentScopes


class SortByData(str, Enum):
    relevance = "relevance"
    alphabetical = "alphabetical"


class TagsWithMetaFields(str, Enum):
    connectorsCount = "connectorsCount"


class SearchFilters(BaseModel):
    tags: dict[str, list[str]] | None = Field(description="Filter by tags.")
    connectors: list[int] | None = Field(description="Filter by connectors.")
    data: dict | None = Field(description="Filter by data.")
    languages: list[str] | None = Field(description="Filter by language.")
    zt_connector_id: int | None = Field(description="ZT connector ID.")
    zt_tree_ids: list[int] | None = Field(description="ZT connector tree ID.")
    zt_tags: list[str] | None = Field(description="ZT agent tags.")
    contentScopeParameters: list[dict, dict] | None = Field(
        description="Content scopes."
    )
    contentScopeFilter: SearchWidgetContentScopes | None = Field(
        description="Content scope filter."
    )


class SearchRequest:
    def __init__(
        self,
        search: str = Query(description="String to search for."),
        orgId: int = Query(description="Organization ID."),
        deploymentId: str = Query(description="Deployment ID of the widget."),
        limit: int | None = Query(
            default=None,
            description="Number of results to use for the answer.",
        ),
        sortBy: SortByData | None = Query(
            default=SortByData.relevance,
            description="Sort by relevance or alphabetical.",
        ),
        filters: Json = Query(
            default={},
            description="Filters for the search.",
        ),
    ):
        self.search = search
        self.org_id = orgId
        self.deployment_id = deploymentId
        self.limit = limit
        self.sort_by = sortBy
        self.filters = filters


class SummarizeRequest:
    def __init__(
        self,
        query: str = Query(description="Query to search for."),
        orgId: int = Query(..., description="Organization ID."),
        deploymentId: str = Query(description="Deployment ID of the widget."),
        options: list[int] | None = Query(
            default=None, description="List of options' IDs to summarize."
        ),
    ):
        self.query = query
        self.org_id = orgId
        self.deployment_id = deploymentId
        self.options = options


class SuggestionsRequest:
    def __init__(
        self,
        search: str = Query(description="String to search for."),
        orgId: int = Query(..., description="Organization ID."),
        deploymentId: str = Query(description="Deployment ID of the widget."),
        limit: int | None = Query(
            default=None, description="Suggestions' limit."
        ),
        filters: Json | None = Query(
            default={},
            description="Filters for the search.",
        ),
    ):
        self.search = search
        self.org_id = orgId
        self.deployment_id = deploymentId
        self.limit = limit
        self.filters = filters


class TagsRequest:
    def __init__(
        self,
        queryOrgId: int | None = Query(
            default=None, description="Organization ID.", alias="orgId"
        ),
        headerOrgId: int | None = Header(
            default=None, description="Organization ID.", alias="x-org-id"
        ),
        withMeta: list[TagsWithMetaFields] = Query(
            default=[], description="Collect meta fields."
        ),
    ):
        self.org_id = headerOrgId or queryOrgId

        if self.org_id is None:
            raise HTTPException(
                status_code=422, detail="Organization ID is required."
            )

        self.with_meta = withMeta


class ConnectorsRequest:
    def __init__(
        self,
        orgId: int = Query(..., description="Organization ID."),
        deploymentId: str | None = Query(
            default=None, description="Deployment ID."
        ),
    ):
        self.org_id = orgId
        self.deployment_id = deploymentId


class DocumentsRequest:
    def __init__(
        self,
        orgId: int | None = Query(
            default=None,
            description="Organization ID. Must be "
            "present if connectorId is not.",
            gt=0,
        ),
        connectorId: int | None = Query(
            default=None,
            title="Connector ID.",
            description="Connector ID. Must be present if orgId is not.",
            gt=0,
        ),
        limit: int | None = Query(
            default=None, description="Must be present if offset is.", gt=0
        ),
        offset: int | None = Query(
            default=None, description="Must be present if limit is.", gt=-1
        ),
    ):
        self.org_id = orgId
        self.connector_id = connectorId
        self.limit = limit
        self.offset = offset


class LanguagesRequest:
    def __init__(
        self,
        orgId: int = Query(..., description="Organization ID."),
    ):
        self.org_id = orgId
