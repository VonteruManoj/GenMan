import re
from abc import ABC, abstractmethod


class Chunker(ABC):
    def __init__(self, max_length, concat_type):
        self.max_length = max_length
        self.concat_type = concat_type

    def create_concat_str(self, data):
        concat_str = ""
        concat_keys = ["title", "description"]
        if self.concat_type in ["prefix", "suffix"]:
            concat_str = " ".join(
                [
                    data[key]
                    for key in concat_keys
                    if key in data.keys() and data[key]
                ]
            )
        return concat_str

    @staticmethod
    def get_snippets(text: str, snippet_len):
        results = []
        for i in range(0, len(text), snippet_len):
            results.append(text[i : i + snippet_len])  # noqa: E203
        return results

    def get_chunk(self, snippet, concat_str):
        if self.concat_type == "prefix":
            return " ".join([concat_str, snippet])
        elif self.concat_type == "suffix":
            return " ".join([snippet, concat_str])
        else:
            return snippet

    @abstractmethod
    def chunk(self, title, text, concat_str):
        pass


class CharacterChunker(Chunker):
    def __init__(self, max_length, concat_type):
        super().__init__(max_length, concat_type)

    def chunk(self, title, text, concat_str):
        chunks = []
        if not self.concat_type or len(concat_str) == 0:
            snippet_len = self.max_length
        else:
            snippet_len = self.max_length - len(concat_str) - 1

        snippets = self.get_snippets(text, snippet_len)

        for snippet in snippets:
            chunk = self.get_chunk(snippet, concat_str)
            chunks.append(chunk)

        if title:
            chunks.append(title)
            snippets.append(title)

        return chunks, snippets


class SentenceChunker(Chunker):
    SENTENCE_PATTERN = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s"

    def __init__(self, max_length, concat_type):
        super().__init__(max_length, concat_type)

    def chunk(self, title, content, concat_str):
        """
        Chunk content by sentences
        """
        chunks = []
        snippets = []
        sentences = re.split(self.SENTENCE_PATTERN, content)
        current_chunk = ""
        for sentence in sentences:
            current_chunk, chunks, snippets = self._process_sentence(
                self.max_length, current_chunk, sentence, concat_str, snippets
            )

        if current_chunk:
            snippets.append(current_chunk)
            current_chunk = self.get_chunk(current_chunk, concat_str)
            chunks.append(current_chunk)

        if title:
            chunks.append(title)
            snippets.append(title)

        return chunks, snippets

    def _process_sentence(
        self, snippet_length, current_chunk, sentence, concat_str, snippets
    ):
        """
        Process a sentence
        """
        chunks = []

        if len(sentence) + len(concat_str) >= snippet_length:
            # This is a very long sentence, we need to split it
            smaller_sentences = self.get_snippets(
                sentence, snippet_length - len(concat_str) - 1
            )
            for smaller_sentence in smaller_sentences:
                # We append to chunks and snippets because the sentences are
                # of the right size
                snippets.append(smaller_sentence)
                smaller_sentence = self.get_chunk(smaller_sentence, concat_str)
                chunks.append(smaller_sentence)

        elif (
            len(current_chunk) + len(sentence) + len(concat_str)
            <= snippet_length
        ):
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
            # We do not append to chunks because it is still too small, and we
            # can try adding more sentences
        else:
            if current_chunk:
                # We append to chunks and snippets because the sentences are
                # of the right size
                snippets.append(current_chunk)
                current_chunk = self.get_chunk(current_chunk, concat_str)
                chunks.append(current_chunk)
            current_chunk = sentence

        return current_chunk, chunks, snippets
