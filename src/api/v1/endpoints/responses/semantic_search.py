from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.endpoints.responses import BaseResponse

tags_example = {"location": ["America", "Asia"]}

document_example = {
    "id": 1,
    "orgId": 1,
    "language": "de",
    "title": "Document title",
    "description": "Example document",
    "tags": tags_example,
    "data": {"specificField": "of the article"},
    "connectorId": 1,
    "articleId": 1,
    "createdAt": "2023-06-13T12:00:00",
    "updatedAt": "2023-06-13T12:30:00",
}


class SemanticSearchDocument(BaseModel):
    id: int
    orgId: int
    language: str | None
    title: str
    description: str | None
    tags: dict
    data: dict
    connectorId: int
    articleId: str
    createdAt: datetime | None
    updatedAt: datetime | None

    class Config:
        schema_extra = {"example": document_example}


class SemanticSearchOption(BaseModel):
    id: int = Field(description="The id of the option")
    snippet: str = Field(description="The snippet of the option")
    distance: float | None
    document: SemanticSearchDocument = Field(
        description="The document of the option"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "snippet": "snippet of text",
                "document": document_example,
            }
        }


class SemanticSearchData(BaseModel):
    options: list[SemanticSearchOption] = Field(
        description="The options closest to the query",
    )
    analyticsId: str = Field(
        description="The id of the analytics batch",
        example="550e8400-e29b-41d4-a716-446655440000",
    )


class SearchResponse(BaseResponse):
    data: SemanticSearchData = Field(
        description="The data of the search",
    )


class SearchSuggestionsResponse(BaseResponse):
    data: list[str] = Field(
        description="The suggestions of the search",
        example=["title", "title description"],
    )


class TagMeta(BaseModel):
    tag: str
    value: str
    connectorId: int
    count: int


class TagsMeta(BaseModel):
    connectorsCount: list[TagMeta] | None = Field(
        description="The metadata of the tags",
        example=[
            {"tag": "location", "value": "us", "connectorId": 1, "count": 2}
        ],
    )


class TagsResponse(BaseResponse):
    data: dict = Field(description="The available tags", example=tags_example)
    meta: TagsMeta | None


class SummarizeAnswerData(BaseModel):
    answer: str = Field(default=..., description="The answer of the search")
    options: list[SemanticSearchOption] = Field(
        description="The options closest to the query",
    )


class SummarizeAnswerResponse(BaseResponse):
    data: SummarizeAnswerData


class ConnectorTypeData(BaseModel):
    name: str
    desc: str | None = Field(..., alias="description")
    provider: str


class ConnectorData(BaseModel):
    id: int
    name: str
    desc: str | None = Field(..., alias="description")
    connectorType: ConnectorTypeData


class ConnectorsResponse(BaseResponse):
    data: list[ConnectorData]


class DocumentsResponse(BaseResponse):
    data: list[SemanticSearchDocument] = Field(
        description="List of documents",
    )


class LanguagesResponse(BaseResponse):
    data: list[str] = Field(
        description="List of languages",
    )
