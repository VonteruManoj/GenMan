import pytest
from pydantic import ValidationError

from src.api.v1.endpoints.responses.semantic_search import (
    ConnectorData,
    ConnectorsResponse,
    ConnectorTypeData,
    DocumentsResponse,
    LanguagesResponse,
    SearchResponse,
    SearchSuggestionsResponse,
    SemanticSearchData,
    SemanticSearchDocument,
    SemanticSearchOption,
    TagsResponse,
)


def test_search_response():
    assert SearchResponse(
        data=SemanticSearchData(
            analyticsId="123-123-123-123",
            options=[
                SemanticSearchOption(
                    id=1,
                    snippet="snippet",
                    distance=0.25,
                    document=SemanticSearchDocument(
                        id=1,
                        orgId=1,
                        language="en",
                        title="title",
                        description="description",
                        tags={"tag-1": ["v1", "v2"]},
                        data={},
                        connectorId=1,
                        articleId="1",
                        createdAt="2021-01-01T00:00:00",
                        updatedAt="2021-01-01T00:00:00",
                    ),
                )
            ],
        )
    )


def test_search_response_missing_fields():
    with pytest.raises(ValidationError):
        SearchResponse()


def test_suggestions_response():
    assert SearchSuggestionsResponse(data=["data"])


def test_suggestions_response_missing_fields():
    with pytest.raises(ValidationError):
        SearchSuggestionsResponse()


def test_tags_response():
    assert TagsResponse(data={"tag-1": ["v1", "v2"]})


def test_tags_response_missing_fields():
    with pytest.raises(ValidationError):
        TagsResponse()


def test_connectors_response():
    assert ConnectorsResponse(
        data=[
            ConnectorData(
                id=1,
                name="name",
                description="desc",
                connectorType=ConnectorTypeData(
                    name="name", description="desc", provider="provider"
                ),
            )
        ]
    )


def test_connectors_response_missing_fields():
    with pytest.raises(ValidationError):
        ConnectorsResponse()


def test_documents_response():
    assert DocumentsResponse(
        data=[
            SemanticSearchDocument(
                id=1,
                orgId=1,
                language="en",
                title="title",
                description="description",
                tags={"tag-1": ["v1", "v2"]},
                data={},
                connectorId=1,
                articleId="1",
                createdAt="2021-01-01T00:00:00",
                updatedAt="2021-01-01T00:00:00",
            )
        ]
    )


def test_documents_response_missing_fields():
    with pytest.raises(ValidationError):
        DocumentsResponse()


def test_languages_response():
    assert LanguagesResponse(data=["en"])


def test_languages_response_missing_fields():
    with pytest.raises(ValidationError):
        LanguagesResponse()
