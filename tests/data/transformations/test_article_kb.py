import copy
from unittest.mock import Mock

import numpy as np

from src.data.chunkers.chunker import CharacterChunker, SentenceChunker
from src.data.transformations.article_kb import (
    BronzeToSilverTransformation,
    SilverToGoldTransformation,
)
from tests.__stubs__.article_kb_templates import BRONZE_SALESFORCE_KB_TEMPLATE


#############################
# Bronze to Silver
#############################
def test_all_keys_are_present():
    transformer = BronzeToSilverTransformation(BRONZE_SALESFORCE_KB_TEMPLATE)
    transformed = transformer.handle()
    assert "articleNumber" in transformed.keys()
    assert "articleType" in transformed.keys()
    assert "content" in transformed.keys()
    assert "contentType" in transformed.keys()
    assert "createdAt" in transformed.keys()
    assert "filePath" in transformed.keys()
    assert "id" in transformed.keys()
    assert "lang" in transformed.keys()
    assert "updatedAt" in transformed.keys()
    assert "publishedAt" in transformed.keys()
    assert "tags" in transformed.keys()
    assert "title" in transformed.keys()
    assert "version" in transformed.keys()


def test_all_text_content_is_the_same_but_normalized():
    data = copy.deepcopy(BRONZE_SALESFORCE_KB_TEMPLATE)
    data["details"] = [
        {"label": "<h1>Title</h1>", "value": "Some <br> Title"},
        {
            "label": "<b>Content</b>",
            "value": '<image src="something">\xe2\x80\x9cSome Content\xe2'
            "Here \x80it \x9dis",
        },
    ]
    transformer = BronzeToSilverTransformation(data)
    transformed = transformer.handle()
    assert transformed["content"] == "Some  Title\nSome ContentHere it is"


def test_html_is_normalized():
    html_text = "<h1>This is a fantactic title!</h1> <p>Test</p>"
    assert (
        BronzeToSilverTransformation._normalize_text(html_text)
        == "This is a fantactic title! Test"
    )


def test_text_has_not_hex_chars():
    hex_text = (
        "\xe2\x80\x9c\x00http://www.google.com\xe2\x80\x9d blah blah#%#@$^blah"
    )
    assert (
        BronzeToSilverTransformation._normalize_text(hex_text)
        == "http://www.google.com blah blah#%#@$^blah"
    )


def test_correct_parse_date():
    date_str = "2023-09-11T08:59:52Z"
    assert (
        BronzeToSilverTransformation._parse_date(date_str)
        == "2023-09-11T08:59:52+00:00"
    )


def test_incorrect_parse_date():
    date_str = "2023-09-11T08:61:52"
    assert BronzeToSilverTransformation._parse_date(date_str) is None


#############################
# Silver to Gold
#############################
def test_concat_text_from_transformation():
    embedder_mock = Mock()
    chunker = SentenceChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"title": "a" * 100, "content": "b" * 100, "lang": "es", "id": "123"},
        embedder_mock,
        chunker,
    )
    content = {
        "title": "a" * 100,
        "content": "b" * 100,
    }
    concat_text = transformation.concat_text(content)
    assert len(concat_text) == 100
    assert concat_text == "b" * 100


def test_chunk_text_from_transformation():
    embedder_mock = Mock()
    chunker = CharacterChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"title": "t" * 5, "lang": "es", "id": "123"},
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
        {"title": "t" * 5, "lang": "es", "id": "123"},
        embedder_mock,
        chunker,
    )
    content = " ".join(["a" * 75, "b" * 75, "c" * 60])
    transformation._chunker.max_length = 100
    snippets = transformation._chunker.get_snippets(
        content, transformation._chunker.max_length
    )

    assert len(snippets) == 3
    assert len(snippets[0]) == 100
    assert len(snippets[1]) == 100

    content = " ".join(["a" * 75, "b" * 75, "c" * 71])
    transformation._chunker.max_length = 100
    snippets = transformation._chunker.get_snippets(
        content, transformation._chunker.max_length
    )
    assert len(snippets) == 3


def test_embed_str_from_transformation():
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.array([1, 2, 3])
    chunker = CharacterChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"title": "t" * 5, "lang": "es", "id": "123"}, embedder_mock, chunker
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
        {"title": "t" * 5, "lang": "es", "id": "123"},
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
    transformation = SilverToGoldTransformation(
        {
            "title": "test title",
            "lang": "es",
            "id": "123",
            "content": "test content",
            "org_id": 1,
            "tags": ['"tag1"."tag"', '"tag2"."tag"'],
            "something": "else",
            "connector_id": "123",
            "document_id": "123",
            "createdAt": "2023-09-11T08:59:52+00:00",
            "updatedAt": "2023-09-11T08:59:52+00:00",
        },
        embedder_mock,
        chunker,
    )
    items = transformation.handle()
    snippet = "test content"
    title_snippet = "test title"
    assert len(items) == 2
    assert "chunk" in items[0].keys()
    assert items[0]["chunk"] == snippet
    assert "snippet" in items[0].keys()
    assert items[0]["snippet"] == snippet
    assert "embeddings" in items[0].keys()
    assert "chunk" in items[1].keys()
    assert items[1]["chunk"] == title_snippet
    assert "snippet" in items[1].keys()
    assert items[1]["snippet"] == title_snippet
    assert "embeddings" in items[1].keys()
    embedder_mock.embed.assert_called_once_with([snippet, title_snippet])
    assert "org_id" in items[0].keys()
    assert items[0]["org_id"] == 1
    assert "language" in items[0].keys()
    assert items[0]["language"] == "es"
    assert "title" in items[0].keys()
    assert items[0]["title"] == "test title"
    assert "description" in items[0].keys()
    assert items[0]["description"] is None
    assert "tags" in items[0].keys()
    assert items[0]["tags"] == ['"tag1"."tag"', '"tag2"."tag"']
    assert "data" in items[0].keys()
    assert items[0]["data"] == {"something": "else"}
    assert "connector_id" in items[0].keys()
    assert items[0]["connector_id"] == "123"
    assert "document_id" in items[0].keys()
    assert items[0]["document_id"] == "123"
    assert "created_at" in items[0].keys()
    assert items[0]["created_at"] == "2023-09-11T08:59:52+00:00"
    assert "updated_at" in items[0].keys()
    assert items[0]["updated_at"] == "2023-09-11T08:59:52+00:00"


def test_get_snippets_from_transformation():
    embedder_mock = Mock()
    chunker = CharacterChunker(10, "none")
    transformation = SilverToGoldTransformation(
        {"title": "t" * 5, "lang": "es", "id": "123"},
        embedder_mock,
        chunker,
    )
    content = "".join(["a" * 10, "b" * 5, "c" * 10 + "d" * 5])
    transformation._chunker.max_length = 10
    snippets = list(
        transformation._chunker.get_snippets(
            content, transformation._chunker.max_length
        )
    )
    assert len(snippets) == 3
    assert snippets[0] == "a" * 10
    assert snippets[1] == "b" * 5 + "c" * 5
    assert snippets[2] == "c" * 5 + "d" * 5
