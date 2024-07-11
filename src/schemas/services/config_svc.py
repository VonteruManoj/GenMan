from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LoaderType(Enum):
    Broadcast = "broadcast"
    InPlace = "in-place"
    Window = "window"


class InTreeAuthMode(Enum):
    ApiKey = "api-key"
    AuthenticatedUser = "authenticated-user"


class InTreePlacement(Enum):
    Top = "top"
    Bottom = "bottom"


class SearchWidgetType(Enum):
    Agent = "agent"
    Customer = "customer"
    Internal = "internal"


class Messaging(BaseModel):
    targetOrigin: str


class SearchWidgetNavigation(BaseModel):
    scriptLoader: LoaderType
    articleLoader: LoaderType
    messaging: Messaging


class SearchWidgetDecisionTree(BaseModel):
    all: bool
    treeIds: list[int]
    displayTags: bool
    listTreesOnStartup: bool
    treeLabel: str


class SearchWidgetExternalSource(BaseModel):
    connectorIds: list[int]


class SearchWidgetEmbedded(BaseModel):
    navigation: SearchWidgetNavigation


class SearchWidgetInTree(BaseModel):
    all: bool
    treeIds: list[int]
    placement: str
    authMode: str
    navigation: SearchWidgetNavigation


class SearchWidgetStandalone(BaseModel):
    url: str
    pageTitle: str
    navigation: SearchWidgetNavigation


class SearchWidgetSourcesConfig(BaseModel):
    decisionTree: SearchWidgetDecisionTree
    externalSource: SearchWidgetExternalSource


class SearchWidgetDeployment(BaseModel):
    standalone: SearchWidgetStandalone
    inTree: SearchWidgetInTree
    embedded: SearchWidgetEmbedded
    salesforce: SearchWidgetEmbedded


class SearchWidgetContentScopeSource(BaseModel):
    tags: list[str]
    action: str
    connectorId: int


class SearchWidgetContentScopeParameter(BaseModel):
    name: str
    value: str


class SearchWidgetContentScopes(BaseModel):
    id: str
    sources: list[SearchWidgetContentScopeSource]
    parameter: SearchWidgetContentScopeParameter


class SearchWidgetMetadataInfo(BaseModel):
    sourcesConfig: SearchWidgetSourcesConfig
    deployment: SearchWidgetDeployment
    contentScopes: Optional[list[SearchWidgetContentScopes]] = Field(None)


class SearchWidget(BaseModel):
    id: int
    name: str
    type: str
    deploymentId: str
    deployStandalone: bool
    deployInTree: bool
    deployEmbedded: bool
    deploySalesforce: bool
    enableDecisionTrees: bool
    enableExternalSources: bool
    orgId: int
    active: bool
    createdAt: str
    updatedAt: str
    metadataInfo: SearchWidgetMetadataInfo
