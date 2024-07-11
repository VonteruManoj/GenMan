import pytest

from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
    SemanticSearchItemFactory,
)


@pytest.mark.usefixtures("refresh_database")
def test_semantic_search_item_mapping_for_analytics_fields():
    item = SemanticSearchItemFactory(
        snippet="test",
    )

    result = item.to_analytics_dict()

    assert result["id"] == item.id
    assert result["snippet"] == "test"
    assert "document" in result
    assert len(result) == 3


def test_semantic_search_document_mapping_for_analytics_fields():
    doc = SemanticSearchDocumentFactory(
        title="title",
        connector_id=1,
        document_id="test",
    )

    result = doc.to_analytics_dict()

    assert result["id"] == doc.id
    assert result["title"] == "title"
    assert result["connectorId"] == 1
    assert result["documentId"] == "test"
    assert len(result) == 4


def test_semantic_search_document_sorting_values():
    doc = SemanticSearchDocumentFactory(
        title="title",
    )

    assert doc.sorting_values() == ["title"]

    doc.data = {"node_id": 123, "nodeId": "Nope"}

    assert doc.sorting_values() == ["title", 123]
