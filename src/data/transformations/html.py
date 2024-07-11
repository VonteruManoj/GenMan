from typing import Dict, List

from src.contracts.data.transformations.silver_to_gold import (
    SilverToGoldTransformationInterface,
)
from src.contracts.embedder import EmbedderInterface
from src.data.chunkers.chunker import Chunker


class SilverToGoldTransformation(SilverToGoldTransformationInterface):
    HTML_CONTENT_KEYS = ["content"]

    HTML_METADATA_KEYS = [
        "html_id",
        "language",
        "url",
        "type",
    ]

    def __init__(
        self,
        data: dict,
        embedder: EmbedderInterface,
        chunker: Chunker,
    ):
        self.data = data
        self.embedder = embedder
        self.chunker = chunker
        self.data[self.HTML_METADATA_KEYS[0]] = self.data.pop("id")
        self.data[self.HTML_METADATA_KEYS[1]] = self.data.pop("lang")
        self.data["description"] = None

    def handle(self) -> List[dict]:
        text_dict = {key: self.data[key] for key in self.HTML_CONTENT_KEYS}
        all_text = self.concat_text(text_dict)

        # prepare snippets
        if not len(all_text):
            if not self.data["title"]:
                return []

        # prepare chunks
        chunks, snippets = self.chunk_text(all_text)
        embeddings = self.embed(chunks)

        additional_data = self.prepare_additional_data()

        return [
            {
                "org_id": self.data["org_id"],
                "language": self.data["language"],
                "title": self.data["title"],
                "description": self.data["description"],
                "tags": [],
                "data": additional_data,
                "connector_id": self.data["connector_id"],
                "document_id": self.data["html_id"],
                "created_at": None,
                "updated_at": None,
                "embeddings": embeddings,
                "snippet": snippet,
                "chunk": chunk,
            }
            for chunk, embeddings, snippet in zip(chunks, embeddings, snippets)
        ]

    def concat_text(self, content: Dict[str, str]) -> str:
        return " ".join(
            [content[key] for key in self.HTML_CONTENT_KEYS if key in content]
        )

    def chunk_text(self, content: str):
        concat_str = self.chunker.create_concat_str(self.data)
        chunks, snippets = self.chunker.chunk(
            self.data["title"], content, concat_str
        )
        return chunks, snippets

    def embed(self, text: List[str] | str) -> List[List[float]]:
        if not self.embedder.connected:
            self.embedder.connect()
        return self.embedder.embed(text)

    def prepare_additional_data(self):
        other_columns = [
            "org_id",
            "language",
            "title",
            "html_id",
            "connector_id",
        ]
        return {
            key: self.data[key]
            for key in self.data.keys()
            if key not in other_columns
        }
