from src.data.chunkers.chunker import CharacterChunker, SentenceChunker


def get_chunker(chunking_method, snippet_length, concat_type):
    chunker = None
    if chunking_method == "sentence":
        chunker = SentenceChunker(snippet_length, concat_type)
    elif chunking_method == "characters":
        chunker = CharacterChunker(snippet_length, concat_type)
    if chunker is None:
        chunker = SentenceChunker(snippet_length, concat_type)
    return chunker
