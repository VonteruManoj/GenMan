import datetime
import string
from typing import Dict, List

from bs4 import BeautifulSoup

from src.contracts.data.transformations.base import BaseTransformationInterface
from src.contracts.data.transformations.silver_to_gold import (
    SilverToGoldTransformationInterface,
)
from src.contracts.embedder import EmbedderInterface
from src.data.chunkers.chunker import Chunker
from src.util.tags_parser import TagParser


class BronzeToSilverTransformation(BaseTransformationInterface):
    DATE_KEY = [
        "createdAt",
        "updatedAt",
        "publishedAt",
    ]

    CONTENT_KEY = "details"

    def __init__(self, data: dict):
        self._data = data

    def handle(self) -> dict:
        processed = {
            k: v
            for k, v in self._data.items()
            if k != self.CONTENT_KEY and k not in self.DATE_KEY
        }

        if "tags" in processed:
            processed["tags"] = TagParser.from_dict(
                {
                    item["name"]: item["values"]
                    for item in processed["tags"]
                    if "values" in item
                }
            ).to_str()
        processed["content"] = self._data[self.CONTENT_KEY]
        processed["content"] = self._normalize_text(
            "\n".join(
                [
                    v["value"]
                    for v in processed["content"]
                    if "value" in v and len(v["value"])
                ]
            )
        )
        for k in self.DATE_KEY:
            if k in self._data:
                processed[k] = self._parse_date(self._data[k])
        return processed

    @staticmethod
    def _parse_date(date_str: str) -> str | None:
        try:
            date = (
                datetime.datetime.fromisoformat(date_str)
                .astimezone(datetime.timezone.utc)
                .isoformat()
            )
        except ValueError:
            date = None
        return date

    @staticmethod
    def _normalize_text(text: str) -> str:
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text()
        printable = set(string.printable)
        text = "".join(filter(lambda x: x in printable, text))
        return text


class SilverToGoldTransformation(SilverToGoldTransformationInterface):
    CONTENT_KEYS = ["content"]

    def __init__(
        self, data: dict, embedder: EmbedderInterface, chunker: Chunker
    ):
        self._data = data
        self._embedder = embedder
        self._chunker = chunker
        self._data["language"] = self._data.pop("lang")
        self._data["document_id"] = self._data.pop("id")

    def handle(self) -> List[dict]:
        text_dict = {key: self._data[key] for key in self.CONTENT_KEYS}
        all_text = self.concat_text(text_dict)

        if not len(all_text):
            if not self._data["title"]:
                return []

        chunks, snippets = self.chunk_text(all_text)
        embeddings = self.embed(chunks)

        additional_data = self.prepare_additional_data()

        return [
            {
                "org_id": self._data["org_id"],
                "language": self._data["language"],
                "title": self._data["title"],
                "description": None,
                "tags": self._data["tags"] if "tags" in self._data else [],
                "data": additional_data,
                "connector_id": self._data["connector_id"],
                "document_id": self._data["document_id"],
                "created_at": self._data["createdAt"],
                "updated_at": (
                    self._data["updatedAt"]
                    if "updatedAt" in self._data
                    else self._data["createdAt"]
                ),
                "embeddings": embedding,
                "chunk": chunk,
                "snippet": snippet,
            }
            for chunk, embedding, snippet in zip(chunks, embeddings, snippets)
        ]

    def concat_text(self, content: Dict[str, str]):
        return " ".join(
            [content[key] for key in self.CONTENT_KEYS if key in content]
        )

    def chunk_text(self, content: str):
        concat_str = self._chunker.create_concat_str(self._data)
        chunks, snippets = self._chunker.chunk(
            self._data["title"], content, concat_str
        )
        return chunks, snippets

    def embed(self, text: List[str] | str) -> List[List[float]]:
        if not self._embedder.connected:
            self._embedder.connect()
        return self._embedder.embed(text)

    def prepare_additional_data(self):
        other_columns = [
            "org_id",
            "language",
            "title",
            "tags",
            "connector_id",
            "document_id",
            "createdAt",
            "updatedAt",
            "content",
        ]
        return {k: v for k, v in self._data.items() if k not in other_columns}
