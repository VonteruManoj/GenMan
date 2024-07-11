import pytest

from src.api.v1.endpoints.requests.semantic_search import (
    ConnectorsRequest,
    LanguagesRequest,
    SearchFilters,
    SearchRequest,
    SuggestionsRequest,
    TagsRequest,
)

plain_full_search_filters = {
    "tags": {
        "t1": ["v1", "v2"],
        "t2": ["v2"],
    },
    "connectors": [1, 2],
}


def test_search_parameters():
    request = SearchRequest(
        search="test",
        orgId=1,
        limit=5,
        sortBy="relevance",
        filters=plain_full_search_filters,
    )

    assert request.search == "test"
    assert request.org_id == 1
    assert request.limit == 5
    assert request.sort_by == "relevance"
    assert request.filters == plain_full_search_filters


def test_suggestions():
    request = SuggestionsRequest(
        search="test", orgId=1, limit=5, filters=plain_full_search_filters
    )

    assert request.search == "test"
    assert request.org_id == 1
    assert request.limit == 5
    assert request.filters == plain_full_search_filters


def test_search_filters():
    o = SearchFilters.parse_obj(plain_full_search_filters)

    assert o.tags == plain_full_search_filters["tags"]
    assert o.connectors == [1, 2]

    with pytest.raises(AttributeError):
        o.not_valid


def test_tags():
    request = TagsRequest(
        queryOrgId=1, headerOrgId=2, withMeta=["connectorsCount"]
    )

    assert request.org_id == 2
    assert request.with_meta == ["connectorsCount"]

    request = TagsRequest(
        queryOrgId=2, headerOrgId=None, withMeta=["connectorsCount"]
    )

    assert request.org_id == 2


def test_connectors_parameters():
    request = ConnectorsRequest(
        orgId=1,
    )

    assert request.org_id == 1


def test_languages_parameters():
    request = LanguagesRequest(
        orgId=1,
    )

    assert request.org_id == 1
