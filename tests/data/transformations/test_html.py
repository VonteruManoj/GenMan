from unittest.mock import Mock

import numpy as np

from src.data.chunkers.chunker import CharacterChunker
from src.data.transformations.html import SilverToGoldTransformation


def test_concat_text_from_transformation():
    embedder_mock = Mock()
    chunker = CharacterChunker(150, "none")
    transformation = SilverToGoldTransformation(
        {"id": "something", "lang": "en", "content": "a" * 100},
        embedder_mock,
        chunker,
    )
    content = {
        "page_title": "a" * 100,
        "content": "b" * 100,
        "question": "c" * 100 + "d" * 15,
    }
    concat_text = transformation.concat_text(content)
    assert len(concat_text) == 100
    assert concat_text == "b" * 100


def test_chunk_text_from_transformation():
    embedder_mock = Mock()
    chunker = CharacterChunker(150, "prefix")
    transformation = SilverToGoldTransformation(
        {"id": "something", "lang": "en", "title": "t" * 5},
        embedder_mock,
        chunker,
    )
    content = " ".join(["a" * 100, "b" * 100, "c" * 100 + "d" * 50])
    chunks, snippets = transformation.chunk_text(content)
    assert len(chunks) == 4
    assert len(chunks[0]) == 150
    assert len(chunks[1]) == 150
    assert len(chunks[2]) == 70

    assert chunks[0] == " ".join(["t" * 5, "a" * 100, "b" * 43])
    assert chunks[1] == " ".join(["t" * 5, "b" * 57, "c" * 86])
    assert chunks[2] == " ".join(["t" * 5, "c" * 14 + "d" * 50])


def test_snippets_with_small_last_snippet_gets_merged_into_previous_one():
    embedder_mock = Mock()
    chunker = CharacterChunker(100, "prefix")
    transformation = SilverToGoldTransformation(
        {"id": "something", "lang": "en", "title": "t" * 5},
        embedder_mock,
        chunker,
    )
    content = " ".join(["a" * 75, "b" * 75, "c" * 60])
    snippets = transformation.chunker.get_snippets(
        content, transformation.chunker.max_length
    )

    assert len(snippets) == 3
    assert len(snippets[0]) == 100
    assert len(snippets[1]) == 100
    assert len(snippets[2]) == 12
    assert snippets[0] == " ".join(["a" * 75, "b" * 24])
    assert snippets[1] == " ".join(["b" * 51, "c" * 48])
    assert snippets[2] == " ".join(["c" * 12])


def test_embed_str_from_transformation():
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.array([1, 2, 3])
    chunker = CharacterChunker(150, "prefix")
    transformation = SilverToGoldTransformation(
        {"id": "something", "lang": "en", "title": "t" * 5},
        embedder_mock,
        chunker,
    )
    transformation.embed("test")
    assert embedder_mock.embed.call_count == 1
    embedder_mock.embed.assert_called_once_with("test")


def test_embed_list_from_transformation():
    embedder_mock = Mock()
    embedder_mock.embed = Mock()
    embedder_mock.embed.return_value = np.array([1, 2, 3])
    chunker = CharacterChunker(150, "prefix")
    transformation = SilverToGoldTransformation(
        {"id": "something", "lang": "en", "title": "t" * 5},
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
    chunker = CharacterChunker(150, "prefix")
    html_id = "something"
    language = "en-US"
    title = "awesome title"
    content = "this is a test content"
    url = "https://www.test.com"
    type_ = "test"
    org_id = 1
    connector_id = 123
    transformation = SilverToGoldTransformation(
        {
            "id": html_id,
            "lang": language,
            "title": title,
            "content": content,
            "url": url,
            "type_": type_,
            "org_id": org_id,
            "connector_id": connector_id,
        },
        embedder_mock,
        chunker,
    )
    items = transformation.handle()
    embedded_text = f"{title} {content}"
    assert len(items) == 2

    assert "org_id" in items[0].keys()
    assert items[0]["org_id"] == org_id
    assert "language" in items[0].keys()
    assert items[0]["language"] == language
    assert "title" in items[0].keys()
    assert items[0]["title"] == title
    assert "description" in items[0].keys()
    assert items[0]["description"] is None
    assert "tags" in items[0].keys()
    assert items[0]["tags"] == []
    assert "data" in items[0].keys()
    assert items[0]["data"] == {
        "content": content,
        "url": url,
        "type_": type_,
        "description": None,
    }
    assert "connector_id" in items[0].keys()
    assert items[0]["connector_id"] == connector_id
    assert "document_id" in items[0].keys()
    assert items[0]["document_id"] == html_id
    assert "created_at" in items[0].keys()
    assert items[0]["created_at"] is None
    assert "updated_at" in items[0].keys()
    assert items[0]["updated_at"] is None
    assert "embeddings" in items[0].keys()
    embedder_mock.embed.assert_called_once_with([embedded_text, title])
    assert "snippet" in items[0].keys()
    assert items[0]["snippet"] == content
    assert "chunk" in items[0].keys()
    assert items[0]["chunk"] == embedded_text
