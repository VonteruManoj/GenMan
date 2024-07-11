from src.data.chunkers.chunker import CharacterChunker, SentenceChunker

character_chunker = CharacterChunker(50, "prefix")
sentence_chunker = SentenceChunker(100, "suffix")


def test_create_concat_str():
    data = {"title": "Hello", "description": "World", "other_key": "Test"}
    concat_str = character_chunker.create_concat_str(data)
    assert concat_str == "Hello World"


def test_get_snippets():
    text = "Hello World test snippets"
    snippets = character_chunker.get_snippets(text, 5)
    expected_snippets = ["Hello", " Worl", "d tes", "t sni", "ppets"]
    assert snippets == expected_snippets


def test_get_chunk():
    snippet = "Hello"
    concat_str = "World"
    chunk_prefix = character_chunker.get_chunk(snippet, concat_str)
    chunk_suffix = sentence_chunker.get_chunk(snippet, concat_str)
    assert chunk_prefix == "World Hello"
    assert chunk_suffix == "Hello World"


def test_chunk_character_chunker():
    character_chunker = CharacterChunker(10, "prefix")
    title = "Hello"
    text = "Hello World test character chunker"
    concat_str = "Test"
    chunks, snippets = character_chunker.chunk(title, text, concat_str)
    expected_chunks = [
        "Test Hello",
        "Test  Worl",
        "Test d tes",
        "Test t cha",
        "Test racte",
        "Test r chu",
        "Test nker",
        "Hello",
    ]
    expected_snippets = [
        "Hello",
        " Worl",
        "d tes",
        "t cha",
        "racte",
        "r chu",
        "nker",
        "Hello",
    ]
    assert chunks == expected_chunks
    assert snippets == expected_snippets


def test_chunk_sentence_chunker():
    sentence_chunker = SentenceChunker(50, "suffix")
    title = "Hello"
    content = "Hello World! What is your name?"
    concat_str = "Test"
    chunks, snippets = sentence_chunker.chunk(title, content, concat_str)
    expected_chunks = ["Hello World! What is your name? Test", "Hello"]
    expected_snippets = ["Hello World! What is your name?", "Hello"]
    assert chunks == expected_chunks
    assert snippets == expected_snippets


def test_small_chunk_sentence_chunker():
    sentence_chunker = SentenceChunker(25, "suffix")
    title = "Hello"
    content = "Hello World! What is your name?"
    concat_str = "Test"
    chunks, snippets = sentence_chunker.chunk(title, content, concat_str)
    expected_chunks = ["Hello World! Test", "What is your name? Test", "Hello"]
    expected_snippets = ["Hello World!", "What is your name?", "Hello"]
    assert chunks == expected_chunks
    assert snippets == expected_snippets
