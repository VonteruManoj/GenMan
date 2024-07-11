import copy
import json
import warnings
from unittest.mock import Mock

import numpy as np
from bs4 import MarkupResemblesLocatorWarning

from src.data.chunkers.chunker import CharacterChunker, SentenceChunker
from src.data.transformations.zt_trees import (
    BronzeToSilverTransformation,
    RawToBronzeTransformation,
    SilverToGoldTransformation,
)
from tests.__stubs__.tree_templates import (
    BRONZE_TREE_METADATA_TEMPLATE,
    BRONZE_TREE_NODES_TEMPLATE,
    RAW_TREE_TEMPLATE_TREE,
)


####################
# Raw To Bronze
####################
def test_tree_has_keys():
    preparer = RawToBronzeTransformation(json.loads(RAW_TREE_TEMPLATE_TREE))
    prepared = preparer.handle()
    assert "nodes" in prepared
    assert "meta" in prepared

    assert "id" in prepared["meta"]
    assert "name" in prepared["meta"]
    assert "description" in prepared["meta"]
    assert "tags" in prepared["meta"]
    assert "org_id" in prepared["meta"]
    assert "active" in prepared["meta"]
    assert "create_date" in prepared["meta"]
    assert "last_opened" in prepared["meta"]
    assert "last_modified" in prepared["meta"]
    assert "is_private" in prepared["meta"]
    assert "language" in prepared["meta"]


def test_nodes_have_keys():
    preparer = RawToBronzeTransformation(json.loads(RAW_TREE_TEMPLATE_TREE))
    prepared = preparer.handle()
    for node in prepared["nodes"].keys():
        assert "page_title" in prepared["nodes"][node]
        assert "content" in prepared["nodes"][node]
        assert "question" in prepared["nodes"][node]
        assert "keywords" in prepared["nodes"][node]
        assert "tag" in prepared["nodes"][node]


def test_content_is_the_same():
    raw_data = json.loads(RAW_TREE_TEMPLATE_TREE)
    preparer = RawToBronzeTransformation(raw_data)
    prepared = preparer.handle()
    for key in prepared["meta"].keys():
        if key == "tags":
            assert prepared["meta"][key] == (
                raw_data[key].split(",") if raw_data[key] else []
            )
        elif key == "active" or key == "is_private":
            assert prepared["meta"][key] == bool(int(raw_data[key]))
        elif key in ["create_date", "last_opened", "last_modified"]:
            assert prepared["meta"][key] == "2023-04-14T19:04:11+00:00"
        else:
            assert prepared["meta"][key] == raw_data[key]
    for node in prepared["nodes"].keys():
        assert (
            prepared["nodes"][node]["content"]
            == raw_data["nodes"][node]["content"]
        )


####################
# Bronze To Silver
####################
def test_all_keys_tree_metadata_remain():
    normalizer = BronzeToSilverTransformation(BRONZE_TREE_METADATA_TEMPLATE)
    prepared_all_keys = BRONZE_TREE_METADATA_TEMPLATE.keys()
    normalized = normalizer.handle()
    assert "content" in normalized.keys()
    assert "metadata" in normalized.keys()
    assert len(normalized["content"]) == 0
    assert len(normalized["metadata"]) != 0
    assert all(
        [key in prepared_all_keys for key in normalized["metadata"].keys()]
    )


def test_all_keys_node_remain():
    normalizer = BronzeToSilverTransformation(BRONZE_TREE_NODES_TEMPLATE)
    prepared_all_keys = BRONZE_TREE_NODES_TEMPLATE.keys()
    normalized = normalizer.handle()
    assert "content" in normalized.keys()
    assert "metadata" in normalized.keys()
    assert len(normalized["metadata"]) != 0
    assert len(normalized["content"]) != 0
    assert all(
        [
            key in prepared_all_keys
            for type_key in normalized.keys()
            for key in normalized[type_key].keys()
        ]
    )


def test_metadata_data_is_the_same_but_normalized():
    normalizer = BronzeToSilverTransformation(BRONZE_TREE_METADATA_TEMPLATE)
    normalized = normalizer.handle()
    for key in normalized["metadata"].keys():
        if key == "name":
            assert normalized["metadata"][key] == "AI Author Assist Test"
        elif key == "description":
            assert normalized["metadata"][key] == "this is some text"
        elif key == "tags":
            assert normalized["metadata"][key] == [
                f'"zt_trees_trees"."{tag}"'
                for tag in BRONZE_TREE_METADATA_TEMPLATE[key]
            ]
        else:
            assert (
                normalized["metadata"][key]
                == BRONZE_TREE_METADATA_TEMPLATE[key]
            )


def test_node_data_is_the_same_but_normalized():
    bronze = copy.deepcopy(BRONZE_TREE_NODES_TEMPLATE)
    bronze["content"] = '<p id="isPasted">This is .\u00f3. node \x20\x21 1</p>'

    normalizer = BronzeToSilverTransformation(bronze)
    normalized = normalizer.handle()
    for type_key in normalized.keys():
        for key in normalized[type_key].keys():
            if key == "page_title":
                assert normalized[type_key][key] == "Paper Airplane"
            elif key == "content":
                assert normalized[type_key][key] == "This is .ó. node  ! 1"
            elif key == "question":
                assert normalized[type_key][key] == "This is a question!"
            else:
                assert (
                    normalized[type_key][key]
                    == BRONZE_TREE_NODES_TEMPLATE[key]
                )


def test_html_is_normalized():
    html_text = "<h1>This is a fantactic title!</h1> <p>Test</p>"
    assert (
        BronzeToSilverTransformation.normalize_text(html_text)
        == "This is a fantactic title! Test"
    )


def test_text_has_not_hex_chars():
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    hex_text = ".\x80 \x80\x9c\x00http://www.google.com \xe2\x80\x9d."
    assert (
        BronzeToSilverTransformation.normalize_text(hex_text)
        == ". http://www.google.com â."
    )
    warnings.filterwarnings("default", category=MarkupResemblesLocatorWarning)


def test_text_has_unicode_chars():
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    hex_text = "This is .\u00f3. node \x20\x21 1."
    assert (
        BronzeToSilverTransformation.normalize_text(hex_text)
        == "This is .ó. node  ! 1."
    )
    warnings.filterwarnings("default", category=MarkupResemblesLocatorWarning)


####################
# Silver To Gold
####################
def test_concat_text_from_transformation():
    embedder_mock = Mock()
    chunker = SentenceChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"page_title": "a" * 100}, {"tag": []}, {}, embedder_mock, chunker
    )
    content = {
        "page_title": "a" * 100,
        "content": "b" * 100,
        "question": "c" * 100 + "d" * 15,
    }
    concat_text = transformation.concat_text(content)
    assert len(concat_text) == 317
    assert concat_text == " ".join(
        ["a" * 100, "b" * 100, "c" * 100 + "d" * 15]
    )


def test_chunk_text_from_transformation():
    embedder_mock = Mock()
    chunker = CharacterChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"page_title": "t" * 5},
        {"tag": []},
        {"tree_name": "a" * 10, "tree_description": "a" * 20},
        embedder_mock,
        chunker,
    )
    content = " ".join(["a" * 100, "b" * 100, "c" * 100 + "d" * 50])
    chunks, snippets = transformation.chunk_text(content)
    assert len(chunks) == 4
    assert len(chunks[0]) == 150
    assert len(chunks[1]) == 150
    assert len(chunks[2]) == 52


def test_snippets_with_small_last_snippet_gets_merged_into_previous_one():
    embedder_mock = Mock()
    chunker = CharacterChunker(100, "none")
    transformation = SilverToGoldTransformation(
        {"page_title": "t" * 5},
        {"tag": []},
        {"tree_name": "a" * 10, "tree_description": "a" * 20},
        embedder_mock,
        chunker,
    )
    content = " ".join(["a" * 75, "b" * 75, "c" * 60])
    transformation.snippet_length = 100
    snippets = transformation.chunker.get_snippets(
        content, transformation.chunker.max_length
    )

    assert len(snippets) == 3
    assert len(snippets[0]) == 100
    assert len(snippets[1]) == 100

    content = " ".join(["a" * 75, "b" * 75, "c" * 71])
    transformation.snippet_length = 100
    snippets = transformation.chunker.get_snippets(
        content, transformation.chunker.max_length
    )
    assert len(snippets) == 3


def test_embed_str_from_transformation():
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.array([1, 2, 3])
    chunker = CharacterChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"page_title": ""}, {"tag": []}, {}, embedder_mock, chunker
    )
    transformation.embed("test")
    assert embedder_mock.embed.call_count == 1
    embedder_mock.embed.assert_called_once_with("test")


def test_embed_list_from_transformation():
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.array([1, 2, 3])
    chunker = SentenceChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"page_title": ""},
        {"tag": []},
        {},
        embedder_mock,
        chunker,
    )
    transformation.embed(["test", "test2"])
    assert embedder_mock.embed.call_count == 1
    embedder_mock.embed.assert_called_once_with(["test", "test2"])


def test_transformation_creates_correct_rows_for_db():
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.array([1, 2, 3])
    chunker = CharacterChunker(150, "none")
    node_title = "test title"
    tree_name = "tree name"
    tree_description = "some tree description"
    language = "en-US"
    org_id = 1
    node_id = "some_node_id"
    tree_id = "7894561237894"
    content = "this is a test content"
    question = "is this a question"
    tree_tags = ['"zt_trees_trees"."test_tag"']
    date = "2023-04-14T19:04:11+00:00"
    connector_id = 123
    transformation = SilverToGoldTransformation(
        {
            "page_title": node_title,
            "content": content,
            "question": question,
        },
        {
            "tag": ["test_tag"],
            "node_id": node_id,
            "some_key": "some text",
            "something": "else",
        },
        {
            "tree_id": tree_id,
            "tree_name": tree_name,
            "tree_description": tree_description,
            "org_id": org_id,
            "language": language,
            "tags": tree_tags,
            "create_date": date,
            "last_modified": date,
            "connector_id": connector_id,
        },
        embedder_mock,
        chunker,
    )
    items = transformation.handle()
    snippet = f"{content} {question}"
    assert len(items) == 2
    assert "org_id" in items[0].keys()
    assert items[0]["org_id"] == org_id
    assert "language" in items[0].keys()
    assert items[0]["language"] == language
    assert "title" in items[0].keys()
    assert items[0]["title"] == f"{tree_name} {node_title}"
    assert "description" in items[0].keys()
    assert items[0]["description"] == tree_description
    assert "tags" in items[0].keys()
    assert items[0]["tags"] == tree_tags
    assert "data" in items[0].keys()
    assert items[0]["data"] == {
        "node_some_key": "some text",
        "node_something": "else",
        "node_tags": ["test_tag"],
        "display": {"title": "tree name", "subtitle": "test title"},
        "tree_id": "7894561237894",
    }
    assert "connector_id" in items[0].keys()
    assert items[0]["connector_id"] == connector_id
    assert "document_id" in items[0].keys()
    assert items[0]["document_id"] == f"{tree_id}::{node_id}"
    assert "created_at" in items[0].keys()
    assert items[0]["created_at"] == date
    assert "updated_at" in items[0].keys()
    assert items[0]["updated_at"] == date
    assert "embeddings" in items[0].keys()
    embedder_mock.embed.assert_called_once_with(
        [snippet, "tree name test title"]
    )
    assert "chunk" in items[0].keys()
    assert items[0]["chunk"] == snippet
    assert "snippet" in items[0].keys()
    assert items[0]["snippet"] == snippet


def test_get_snippets_from_transformation():
    embedder_mock = Mock()
    chunker = CharacterChunker(10, "none")
    transformation = SilverToGoldTransformation(
        {"page_title": ""},
        {"tag": []},
        {},
        embedder_mock,
        chunker,
    )
    content = "".join(["a" * 10, "b" * 5, "c" * 10 + "d" * 5])
    transformation.snippet_length = 10
    snippets = list(
        transformation.chunker.get_snippets(
            content, transformation.chunker.max_length
        )
    )
    assert len(snippets) == 3
    assert snippets[0] == "a" * 10
    assert snippets[1] == "b" * 5 + "c" * 5
    assert snippets[2] == "c" * 5 + "d" * 5


empty_variations = [
    (
        ["page_title"],
        [
            "tree name some tree description this is a test content is this",
            "tree name some tree description  a question",
        ],
    ),
    (
        ["page_title", "content"],
        ["tree name some tree description is this a question"],
    ),
    (["page_title", "content", "question"], []),
    (
        ["content"],
        ["tree name some tree description test title is this a question"],
    ),
    (["content", "question"], ["tree name some tree description test title"]),
    (
        ["question"],
        ["tree name some tree description test title this is a test content"],
    ),
]
