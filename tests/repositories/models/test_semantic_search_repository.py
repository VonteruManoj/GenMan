import os
import random
from unittest.mock import Mock

import pytest

from src.api.v1.endpoints.requests.semantic_search import SearchFilters
from src.core.containers import container
from src.models.semantic_search_item import SemanticSearchDocument
from src.schemas.services.config_svc import SearchWidget
from src.schemas.services.connectors_svc import Connector, ConnectorType
from src.util.tags_parser import TagParser
from tests.__factories__.models.semantic_search import (
    SemanticSearchDocumentFactory,
)

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


def create_widget_valid_items():
    config_svc_mock = Mock()
    config_svc_mock.get_search_widget_by_deployment_id.return_value = (
        SearchWidget.parse_obj(
            {
                "id": 1,
                "name": "widget",
                "type": "agent",
                "deploymentId": "9a44ad83-a9d2-427d-a8c9-91040d2b6e84",
                "deployStandalone": True,
                "deployInTree": True,
                "deployEmbedded": True,
                "deploySalesforce": True,
                "enableDecisionTrees": True,
                "enableExternalSources": True,
                "orgId": 1,
                "active": True,
                "createdAt": "2023-11-13T12:28:21Z",
                "updatedAt": "2023-11-13T12:38:54Z",
                "metadataInfo": {
                    "sourcesConfig": {
                        "decisionTree": {
                            "all": True,
                            "treeIds": [1, 2],
                            "displayTags": True,
                            "listTreesOnStartup": False,
                            "treeLabel": "Scripts",
                        },
                        "externalSource": {"connectorIds": [1, 2]},
                    },
                    "deployment": {
                        "standalone": {
                            "url": "https://zingtree.com/alpha-search",
                            "pageTitle": "My Search",
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            },
                        },
                        "inTree": {
                            "all": True,
                            "treeIds": [1, 2],
                            "placement": "top",
                            "authMode": "authenticated-user",
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            },
                        },
                        "embedded": {
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            }
                        },
                        "salesforce": {
                            "navigation": {
                                "scriptLoader": "window",
                                "articleLoader": "window",
                                "messaging": {"targetOrigin": "*"},
                            }
                        },
                    },
                },
            }
        )
    )

    connectors_svc_mock = Mock()
    ctzt = ConnectorType(
        id=1, name="test", description="test", provider="zingtree", active=True
    )
    ctsfk = ConnectorType(
        id=1,
        name="test",
        description="test",
        provider="salesforce",
        active=True,
    )
    c1 = Connector(
        id=1, name="test", description="test", active=True, connector_type=ctzt
    )
    c2 = Connector(
        id=2,
        name="test",
        description="test",
        active=True,
        connector_type=ctsfk,
    )

    connectors_svc_mock.get_all_connectors.return_value = [c1, c2]

    return config_svc_mock, connectors_svc_mock


@pytest.mark.usefixtures("class_refresh_database")
class TestSemanticSearchRepository:
    @classmethod
    def setup_class(cls):
        cls.semantic_search_repository = container.semantic_search_repository()

    @pytest.mark.usefixtures("refresh_database")
    def test_create_document(self):
        tags = ['"tag-1"."v1"', '"tag-1"."v2"']

        document = self.semantic_search_repository.create_document(
            101,
            "de",
            "title",
            "description",
            tags,
            {"wow": "data"},
            111,
            "d12345",
        )

        assert document is not None
        assert document.id is not None
        assert document.org_id == 101
        assert document.language == "de"
        assert document.title == "title"
        assert document.description == "description"
        assert document.tags == tags
        assert document.data == {"wow": "data"}
        assert document.connector_id == 111
        assert document.document_id == "d12345"

    @pytest.mark.usefixtures("refresh_database")
    def test_create_item(self):
        document = SemanticSearchDocumentFactory(items=0)
        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        chunk = "chunk"
        snippet = "snippet"

        item = self.semantic_search_repository.create_item(
            embeddings, chunk, snippet, document
        )

        assert item is not None
        assert item.id is not None
        assert item.chunk == "chunk"
        assert item.snippet == "snippet"
        assert item.document_id == document.id

    @pytest.mark.usefixtures("refresh_database")
    def test_search_without_items(self):
        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        org_id = 1
        limit = 5
        filters = SearchFilters(connectors=[1])

        options, distances = self.semantic_search_repository.search(
            embeddings, org_id, filters, limit
        )

        assert options == []
        assert distances == []

    @pytest.mark.usefixtures("refresh_database")
    def test_search(self):
        SemanticSearchDocumentFactory.create_batch(
            3, items=5, org_id=1, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, items=5, org_id=2, connector_id=1
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        filters = SearchFilters(connectors=[1])

        # 5 documents with 5 items each
        # odds are from org 1, evens are from org 2
        # odds will have 3 zt_trees * 5 items = 15 items
        # with dedup in place we should get 3
        options, distances = self.semantic_search_repository.search(
            embeddings, 1, filters, None
        )
        assert len(options) == 3
        assert len(distances) == 3

        # and evens will have 2 zt_trees * 5 items = 10 items
        # with dedup in place we should get 2
        options, distances = self.semantic_search_repository.search(
            embeddings, 2, filters, None
        )
        assert len(options) == 2
        assert len(distances) == 2

    @pytest.mark.usefixtures("refresh_database")
    def test_search_treshold(self, override_settings):
        SemanticSearchDocumentFactory.create_batch(
            3, items=5, org_id=1, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, items=5, org_id=2, connector_id=1
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        filters = SearchFilters(connectors=[1])

        with override_settings(SEMANTIC_SEARCH_THRESHOLD=0.0):
            options, distances = self.semantic_search_repository.search(
                embeddings, 1, filters, None
            )
        assert len(options) == 0
        assert len(distances) == 0

    @pytest.mark.usefixtures("refresh_database")
    def test_search_with_limit(self):
        SemanticSearchDocumentFactory.create_batch(
            3, items=5, org_id=1, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, items=5, org_id=2, connector_id=1
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        filters = SearchFilters(connectors=[1])

        options, distances = self.semantic_search_repository.search(
            embeddings, 1, filters, None
        )
        assert len(options) == 3

        options, distances = self.semantic_search_repository.search(
            embeddings, 1, filters, 2
        )
        assert len(options) == 2

    @pytest.mark.usefixtures("refresh_database")
    def test_search_is_filtered_by_tags(self):
        tags = TagParser({"tag-1": ["t1", "t2"]}).to_str()
        SemanticSearchDocumentFactory(
            org_id=1, tags=tags, items=2, connector_id=1
        )
        tags = TagParser({"tag-1": ["t2"], "tag-2": ["a"]}).to_str()
        SemanticSearchDocumentFactory(
            org_id=1, tags=tags, items=2, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=3, items=2, connector_id=1
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        org_id = 1
        filters = SearchFilters.parse_obj(
            {"tags": {"tag-1": ["t1"]}, "connectors": [1]}
        )
        options, distances = self.semantic_search_repository.search(
            embeddings, org_id, filters, None
        )
        assert len(options) == 1

        filters = SearchFilters.parse_obj(
            {"tags": {"tag-1": ["t2"]}, "connectors": [1]}
        )
        options, distances = self.semantic_search_repository.search(
            embeddings, org_id, filters, None
        )
        assert len(options) == 2

        filters = SearchFilters.parse_obj(
            {"tags": {"tag-1": ["t1"], "tag-2": ["a"]}, "connectors": [1]}
        )
        options, distances = self.semantic_search_repository.search(
            embeddings, org_id, filters, None
        )
        assert len(options) == 2

    @pytest.mark.usefixtures("refresh_database")
    def test_search_is_filtered_by_connectors(self):
        SemanticSearchDocumentFactory(items=5, connector_id=1, org_id=1)
        SemanticSearchDocumentFactory(items=5, connector_id=2, org_id=1)
        SemanticSearchDocumentFactory(items=5, connector_id=1, org_id=1)
        SemanticSearchDocumentFactory.create_batch(2, items=5, org_id=2)

        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        filters = SearchFilters(connectors=[1])

        options, distances = self.semantic_search_repository.search(
            embeddings, 1, filters, None
        )
        assert len(options) == 2
        assert options[0].document.connector_id == 1
        assert options[1].document.connector_id == 1

    @pytest.mark.parametrize(
        ("filters_dict", "results_expected"),
        [
            (None, 3),
            ({}, 3),
            ({"Nope!": "value"}, 0),
            ({"str": "wrong-value"}, 0),
            ({"str": "value"}, 1),
            ({"int": 1}, 0),
            ({"int": 10}, 1),
            ({"arr": "value1"}, 0),
            ({"str": "value", "int": 10}, 1),
            ({"str": "value", "int": 1}, 0),
            (
                {
                    "int": 1,
                    "arr": ["asd", "fgh"],
                },
                0,
            ),
            ({"int": [9, 99]}, 2),
            ({"int": [9, 100]}, 1),
            ({"str": [9, 99]}, 0),
            ({"str": [9, 100]}, 0),
            ({"int": ["9", "99"]}, 0),
            ({"int": ["9", "100"]}, 0),
            ({"str": ["9", "99"]}, 2),
            ({"str": ["9", "100"]}, 1),
        ],
    )
    @pytest.mark.usefixtures("refresh_database")
    def test_search_is_filtered_by_data(
        self, filters_dict: dict, results_expected: int
    ):
        SemanticSearchDocumentFactory(
            items=5,
            org_id=1,
            data={
                "str": "value",
                "int": 10,
                "nested": {
                    "nested1": 255,
                },
                "arr": ["asd", "fgh"],
            },
            connector_id=1,
        )

        SemanticSearchDocumentFactory(
            items=5,
            org_id=1,
            data={
                "int": 9,
                "str": "9",
            },
            connector_id=1,
        )

        SemanticSearchDocumentFactory(
            items=5,
            org_id=1,
            data={"int": 99, "str": "99", "n": {"l": 77}},
            connector_id=1,
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]

        options, distances = self.semantic_search_repository.search(
            embeddings,
            1,
            SearchFilters(connectors=[1], data=filters_dict),
            None,
        )
        assert len(options) == results_expected

    @pytest.mark.usefixtures("refresh_database")
    def test_search_is_filtered_by_not_supported_data(self, check_log_message):
        SemanticSearchDocumentFactory(
            items=5,
            org_id=1,
            data={
                "str": "value",
                "int": 10,
                "nested": {
                    "nested1": 255,
                },
                "arr": ["asd", "fgh"],
            },
            connector_id=1,
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]

        options, distances = self.semantic_search_repository.search(
            embeddings,
            1,
            SearchFilters(connectors=[1], data={"ok": {"ok2": "ok3"}}),
            None,
        )
        assert len(options) == 1
        check_log_message(
            "WARNING",
            'Search filter not supported: {"key": "ok",'
            ' "value": {"ok2": "ok3"}}',
        )

        options, distances = self.semantic_search_repository.search(
            embeddings,
            1,
            SearchFilters(connectors=[1], data={"ok": [{"ok2": "ok3"}]}),
            None,
        )
        assert len(options) == 1
        check_log_message(
            "WARNING",
            'Search filter not supported: {"key": "ok",'
            ' "value": [{"ok2": "ok3"}]}',
        )

    @pytest.mark.usefixtures("refresh_database")
    def test_search_is_filtered_by_language(self):
        SemanticSearchDocumentFactory(
            items=5, org_id=1, language="en", title="title", connector_id=1
        )
        SemanticSearchDocumentFactory(
            items=5, org_id=1, language="en-US", title="title", connector_id=1
        )
        SemanticSearchDocumentFactory(
            items=5, org_id=1, language="de", title="title", connector_id=1
        )
        SemanticSearchDocumentFactory(
            items=5, org_id=1, language="en", title="title", connector_id=1
        )
        SemanticSearchDocumentFactory(
            items=5, org_id=1, language="de-AL", title="title", connector_id=1
        )
        SemanticSearchDocumentFactory(
            items=5,
            org_id=1,
            language="eN-Nope",
            title="title",
            connector_id=1,
        )
        SemanticSearchDocumentFactory.create_batch(2, items=5, org_id=2)

        embeddings = [random.random() for _ in range(embeddings_dimensions)]

        options, distances = self.semantic_search_repository.search(
            embeddings,
            1,
            SearchFilters(connectors=[1], languages=["en"]),
            None,
        )
        assert len(options) == 3
        valid_languages = ["en", "en-US"]
        assert options[0].document.language in valid_languages
        assert options[0].document.language in valid_languages
        assert options[1].document.language in valid_languages

    @pytest.mark.usefixtures("refresh_database")
    def test_get_tags(self):
        tags = TagParser({"tag-1": ["t1", "t2"]}).to_str()
        SemanticSearchDocumentFactory(org_id=1, tags=tags, items=2)
        tags = TagParser({"tag-1": ["t2"], "tag-2": ["a"]}).to_str()
        SemanticSearchDocumentFactory(org_id=1, tags=tags, items=2)
        SemanticSearchDocumentFactory.create_batch(2, org_id=3, items=2)

        tags = self.semantic_search_repository.get_tags(1)
        tags = TagParser.from_str(tags).tags

        assert len(tags) == 2
        assert "tag-1" in tags
        assert "tag-2" in tags
        assert len(tags["tag-1"]) == 2
        assert len(tags["tag-2"]) == 1
        assert "t1" in tags["tag-1"]
        assert "t2" in tags["tag-1"]
        assert "a" in tags["tag-2"]

    @pytest.mark.usefixtures("refresh_database")
    def test_get_suggestions(self):
        SemanticSearchDocumentFactory(
            org_id=1, title="Hola", items=2, connector_id=1
        )
        SemanticSearchDocumentFactory(
            org_id=1, description="Hola!", items=2, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=3, items=2, connector_id=2
        )

        suggestions = self.semantic_search_repository.get_search_suggestions(
            search="hola",
            org_id=1,
            filters=SearchFilters(connectors=[1]),
            limit=5,
        )

        assert len(suggestions) == 2
        assert suggestions == ["Hola", "Hola!"]

    @pytest.mark.usefixtures("refresh_database")
    def test_get_suggestions_is_filtered_by_tags(self):
        tags = TagParser({"tag-1": ["t1", "t2"]}).to_str()
        SemanticSearchDocumentFactory(
            org_id=1, tags=tags, title="Hola", items=2, connector_id=1
        )
        tags = TagParser({"tag-1": ["t2"], "tag-2": ["a"]}).to_str()
        SemanticSearchDocumentFactory(
            org_id=1, tags=tags, description="Hola!", items=2, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=3, items=2, connector_id=2
        )

        filters = SearchFilters.parse_obj(
            {"tags": {"tag-1": ["t1"]}, "connectors": [1]}
        )
        suggestions = self.semantic_search_repository.get_search_suggestions(
            search="hola",
            org_id=1,
            filters=filters,
            limit=5,
        )
        assert len(suggestions) == 1
        assert suggestions == ["Hola"]

        filters = SearchFilters.parse_obj(
            {"tags": {"tag-1": ["t2"]}, "connectors": [1]}
        )
        suggestions = self.semantic_search_repository.get_search_suggestions(
            search="hola",
            org_id=1,
            filters=filters,
            limit=5,
        )
        assert len(suggestions) == 2
        assert suggestions == ["Hola", "Hola!"]

        filters = SearchFilters.parse_obj(
            {"tags": {"tag-1": ["t1"], "tag-2": ["a"]}, "connectors": [1]}
        )
        suggestions = self.semantic_search_repository.get_search_suggestions(
            search="hola",
            org_id=1,
            filters=filters,
            limit=5,
        )
        assert len(suggestions) == 2
        assert suggestions == ["Hola", "Hola!"]

    @pytest.mark.usefixtures("refresh_database")
    def test_get_suggestions_is_filtered_by_connectors(self):
        SemanticSearchDocumentFactory(
            items=5, connector_id=1, description="Hola", org_id=1
        )
        SemanticSearchDocumentFactory(
            items=5, connector_id=2, description="Hola!!", org_id=1
        )
        SemanticSearchDocumentFactory(
            items=5, connector_id=1, description="Hola!", org_id=1
        )
        SemanticSearchDocumentFactory.create_batch(2, items=5, org_id=2)

        suggestions = self.semantic_search_repository.get_search_suggestions(
            search="hOla",
            org_id=1,
            filters=SearchFilters(connectors=[1]),
            limit=5,
        )

        assert len(suggestions) == 2
        assert suggestions == ["Hola", "Hola!"]

    @pytest.mark.usefixtures("refresh_database")
    def test_get_suggestions_is_filtered_by_language(self):
        SemanticSearchDocumentFactory(
            items=5,
            language="en",
            description="Hola",
            org_id=1,
            connector_id=1,
        )
        SemanticSearchDocumentFactory(
            items=5,
            language="de",
            description="Hola!!",
            org_id=1,
            connector_id=1,
        )
        SemanticSearchDocumentFactory(
            items=5,
            language="en",
            description="Hola!",
            org_id=1,
            connector_id=1,
        )
        SemanticSearchDocumentFactory.create_batch(
            2, items=5, org_id=2, connector_id=2
        )

        suggestions = self.semantic_search_repository.get_search_suggestions(
            search="hOla",
            org_id=1,
            filters=SearchFilters(connectors=[1], languages=["en"]),
            limit=5,
        )

        assert len(suggestions) == 2
        assert suggestions == ["Hola", "Hola!"]

    @pytest.mark.usefixtures("refresh_database")
    def test_get_documents_invalid_values(self):
        with pytest.raises(ValueError):
            self.semantic_search_repository.get_documents(
                org_id=None,
                connector_id=None,
                limit=None,
                offset=None,
            )

        with pytest.raises(ValueError):
            self.semantic_search_repository.get_documents(
                org_id=1,
                connector_id=None,
                limit=1,
                offset=None,
            )

        with pytest.raises(ValueError):
            self.semantic_search_repository.get_documents(
                org_id=1,
                connector_id=None,
                limit=None,
                offset=1,
            )

    @pytest.mark.usefixtures("refresh_database")
    def test_get_documents_by_org_id(self):
        SemanticSearchDocumentFactory.create_batch(3, org_id=1, items=2)
        SemanticSearchDocumentFactory.create_batch(2, org_id=2, items=2)

        docs = self.semantic_search_repository.get_documents(
            org_id=1,
            connector_id=None,
            limit=None,
            offset=None,
        )
        assert len(docs) == 3
        for doc in docs:
            assert doc.org_id == 1
            assert isinstance(doc, SemanticSearchDocument)

        docs = self.semantic_search_repository.get_documents(
            org_id=2,
            connector_id=None,
            limit=None,
            offset=None,
        )
        assert len(docs) == 2
        for doc in docs:
            assert doc.org_id == 2
            assert isinstance(doc, SemanticSearchDocument)

    @pytest.mark.usefixtures("refresh_database")
    def test_get_documents_by_connector_id(self):
        SemanticSearchDocumentFactory.create_batch(3, connector_id=1, items=2)
        SemanticSearchDocumentFactory.create_batch(2, connector_id=2, items=2)

        docs = self.semantic_search_repository.get_documents(
            org_id=None,
            connector_id=1,
            limit=None,
            offset=None,
        )
        assert len(docs) == 3
        for doc in docs:
            assert doc.connector_id == 1
            assert isinstance(doc, SemanticSearchDocument)

        docs = self.semantic_search_repository.get_documents(
            org_id=None,
            connector_id=2,
            limit=None,
            offset=None,
        )
        assert len(docs) == 2
        for doc in docs:
            assert doc.connector_id == 2
            assert isinstance(doc, SemanticSearchDocument)

    @pytest.mark.usefixtures("refresh_database")
    def test_get_documents_paginated(self):
        docs = SemanticSearchDocumentFactory.create_batch(
            10, connector_id=1, items=2
        )
        SemanticSearchDocumentFactory.create_batch(2, connector_id=2, items=2)

        got = self.semantic_search_repository.get_documents(
            org_id=None,
            connector_id=1,
            limit=4,
            offset=2,
        )
        assert len(got) == 4
        for doc in got:
            assert doc.connector_id == 1
            assert isinstance(doc, SemanticSearchDocument)

        assert got[0].id == docs[2].id
        assert got[1].id == docs[3].id
        assert got[2].id == docs[4].id
        assert got[3].id == docs[5].id

        got = self.semantic_search_repository.get_documents(
            org_id=None,
            connector_id=1,
            limit=2,
            offset=3,
        )
        assert len(got) == 2
        for doc in got:
            assert doc.connector_id == 1
            assert isinstance(doc, SemanticSearchDocument)

        assert got[0].id == docs[3].id
        assert got[1].id == docs[4].id

    @pytest.mark.usefixtures("refresh_database")
    def test_search_best(self):
        SemanticSearchDocumentFactory.create_batch(
            3, items=5, org_id=1, connector_id=1
        )
        SemanticSearchDocumentFactory.create_batch(
            2, items=5, org_id=2, connector_id=1
        )

        embeddings = [random.random() for _ in range(embeddings_dimensions)]
        filters = SearchFilters(connectors=[1])

        # 5 documents with 5 items each
        # odds are from org 1, evens are from org 2
        # odds will have 3 zt_trees * 5 items = 15 items
        options = self.semantic_search_repository.search_best(
            embeddings, 1, filters, None
        )
        assert len(options) == 15

        # and evens will have 2 zt_trees * 5 items = 10 items
        # with dedup in place we should get 2
        options = self.semantic_search_repository.search_best(
            embeddings, 2, filters, None
        )
        assert len(options) == 10

    def test_find_semantic_search_item_by_id(self):
        document = SemanticSearchDocumentFactory(items=1, org_id=1)
        item = document.items[0]

        found_item = (
            self.semantic_search_repository.find_semantic_search_item_by_id(
                item.id, org_id=1
            )
        )

        assert found_item is not None
        assert found_item.id == item.id
        assert found_item.document_id == document.id
        assert found_item.document.id == document.id
        assert found_item.document.items[0].id == item.id

    def test_find_semantic_search_item_by_ids(self):
        document = SemanticSearchDocumentFactory(items=1)
        item = document.items[0]

        found_items = (
            self.semantic_search_repository.find_semantic_search_items_by_ids(
                [item.id], document.org_id
            )
        )

        assert len(found_items) == 1
        assert found_items[0].id == item.id
        assert found_items[0].document_id == document.id
        assert found_items[0].document.id == document.id
        assert found_items[0].document.items[0].id == item.id

    @pytest.mark.usefixtures("refresh_database")
    def test_get_languages(self):
        SemanticSearchDocumentFactory.create_batch(
            3, org_id=1, items=2, language="en"
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=1, items=2, language="de"
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=1, items=2, language="fr"
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=2, items=2, language="en"
        )
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=2, items=2, language="de"
        )

        languages = self.semantic_search_repository.get_languages(1)
        assert len(languages) == 3
        assert "en" in languages
        assert "de" in languages
        assert "fr" in languages

        languages = self.semantic_search_repository.get_languages(2)
        assert len(languages) == 2
        assert "en" in languages
        assert "de" in languages

    @pytest.mark.usefixtures("refresh_database")
    def test_deployment_has_documents(self):
        SemanticSearchDocumentFactory.create_batch(
            2, org_id=2, items=2, language="de", connector_id=1
        )

        flag = self.semantic_search_repository.deployment_has_documents(
            1,
            SearchFilters(connectors=[1]),
        )
        assert flag is False

        flag = self.semantic_search_repository.deployment_has_documents(
            2,
            SearchFilters(connectors=[1]),
        )
        assert flag is True
