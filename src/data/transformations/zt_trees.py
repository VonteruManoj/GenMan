import datetime
import re
from typing import Dict, List

from bs4 import BeautifulSoup

from src.contracts.data.transformations.base import BaseTransformationInterface
from src.contracts.data.transformations.silver_to_gold import (
    SilverToGoldTransformationInterface,
)
from src.contracts.embedder import EmbedderInterface
from src.core.deps.logger import with_logger
from src.data.chunkers.chunker import Chunker
from src.util.tags_parser import TagParser


class RawToBronzeTransformation(BaseTransformationInterface):
    TREE_KEEP_KEYS = [
        "id",
        "name",
        "description",
        "tags",
        "org_id",
        "active",
        "create_date",
        "last_opened",
        "last_modified",
        "is_private",
        "language",
    ]
    NODE_KEEP_KEYS = [
        "page_title",
        "content",
        "question",
        "keywords",
        "tag",
    ]
    TREE_DATE_KEYS = [
        "create_date",
        "last_opened",
        "last_modified",
    ]
    NODES_KEY = "nodes"
    NODE_TYPE_KEY = "type"
    META_KEY = "meta"

    def __init__(self, tree_json: dict):
        self.tree = tree_json

    def handle(self) -> dict:
        prepared = dict()

        # Add meta keys-values
        prepared[self.META_KEY] = {
            key: self.tree[key] for key in self.TREE_KEEP_KEYS
        }

        # Cast meta keys-values
        prepared[self.META_KEY]["tags"] = (
            prepared[self.META_KEY]["tags"].split(",")
            if prepared[self.META_KEY].get("tags")
            else []
        )
        prepared[self.META_KEY]["active"] = bool(
            int(prepared[self.META_KEY]["active"])
        )
        prepared[self.META_KEY]["is_private"] = bool(
            int(prepared[self.META_KEY]["is_private"])
        )

        # Cast meta date keys-values to UTC
        for date_key in self.TREE_DATE_KEYS:
            try:
                prepared[self.META_KEY][date_key] = (
                    datetime.datetime.fromisoformat(
                        prepared[self.META_KEY][date_key]
                    )
                    .astimezone(datetime.timezone.utc)
                    .isoformat()
                )
            except ValueError:
                prepared[self.META_KEY][date_key] = None

        # Extract content nodes
        prepared[self.NODES_KEY] = {
            key: value
            for key, value in self.tree[self.NODES_KEY].items()
            if value[self.NODE_TYPE_KEY] == "Content"
        }

        # Add keys-values from content nodes
        for node in prepared[self.NODES_KEY].keys():
            prepared[self.NODES_KEY][node] = {
                key: prepared[self.NODES_KEY][node][key]
                for key in self.NODE_KEEP_KEYS
            }
            prepared[self.NODES_KEY][node]["keywords"] = (
                prepared[self.NODES_KEY][node]["keywords"].split(",")
                if prepared[self.NODES_KEY][node].get("keywords")
                else []
            )
            prepared[self.NODES_KEY][node]["tag"] = (
                prepared[self.NODES_KEY][node]["tag"].split(",")
                if prepared[self.NODES_KEY][node].get("tag")
                else []
            )

        return prepared


class BronzeToSilverTransformation(BaseTransformationInterface):
    TREE_CONTENT_KEYS = [
        "name",
        "description",
    ]

    NODE_CONTENT_KEYS = [
        "page_title",
        "content",
        "question",
    ]

    TAGS_KEY = "tags"

    def __init__(self, content_json: dict):
        self.json = content_json

    def handle(self) -> dict:
        content = dict()
        metadata = dict()
        for key in self.json.keys():
            if key in self.TREE_CONTENT_KEYS:
                metadata[key] = self.normalize_text(self.json[key])
            elif key in self.NODE_CONTENT_KEYS:
                content[key] = self.normalize_text(self.json[key])
            elif key == self.TAGS_KEY:
                metadata[key] = TagParser.from_dict(
                    {"zt_trees_trees": self.json[key]}
                ).to_str()
            else:
                metadata[key] = self.json[key]

        data = dict(content=content, metadata=metadata)
        return data

    @staticmethod
    def normalize_text(text: str) -> str:
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text()
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]", "", text)


@with_logger()
class SilverToGoldTransformation(SilverToGoldTransformationInterface):
    TREE_CONTENT_KEYS = [
        "tree_name",
        "tree_description",
    ]

    NODE_CONTENT_KEYS = [
        "page_title",
        "content",
        "question",
    ]

    def __init__(
        self,
        content_json: dict,
        node_meta_json: dict,
        tree_meta_json: dict,
        embedder: EmbedderInterface,
        chunker: Chunker,
    ):
        self.content_json = content_json
        self.node_meta_json = node_meta_json
        self.tree_meta_json = tree_meta_json
        self.embedder = embedder
        self.chunker = chunker
        self.node_meta_json["tags"] = node_meta_json.pop("tag")
        self.node_meta_json["page_title"] = content_json["page_title"]

    def handle(self) -> List[dict]:
        # prepare text
        if self.content_json["content"]:
            all_text = " ".join(
                [
                    s
                    for s in [
                        self.content_json["content"],
                        self.content_json["question"],
                    ]
                    if s
                ]
            )
        else:
            if (
                self.content_json["question"]
                or self.content_json["page_title"]
            ):
                all_text = " ".join(
                    [
                        s
                        for s in [
                            self.tree_meta_json["tree_name"],
                            self.content_json["page_title"],
                            self.content_json["question"],
                        ]
                        if s
                    ]
                )
            else:
                all_text = ""

        # prepare snippets
        if not len(all_text):
            if not self.content_json[self.NODE_CONTENT_KEYS[0]]:
                return []
            else:
                all_text = self.content_json[self.NODE_CONTENT_KEYS[0]]

        chunks, snippets = self.chunk_text(all_text)
        embeddings = self.embed(chunks)

        additional_data = self.prepare_additional_data()

        return [
            {
                "org_id": self.tree_meta_json["org_id"],
                "language": self.tree_meta_json["language"],
                "title": " ".join(
                    [
                        self.tree_meta_json["tree_name"],
                        self.node_meta_json["page_title"],
                    ]
                ),
                "description": self.tree_meta_json["tree_description"],
                "tags": self.tree_meta_json["tags"],
                "data": additional_data,
                "connector_id": self.tree_meta_json["connector_id"],
                "document_id": self.get_document_id(),
                "created_at": self.tree_meta_json["create_date"],
                "updated_at": self.tree_meta_json["last_modified"],
                "embeddings": embedding,
                "chunk": chunk,
                "snippet": snippet,
            }
            for chunk, embedding, snippet in zip(chunks, embeddings, snippets)
        ]

    def concat_text(self, content: Dict[str, str]) -> str:
        return " ".join(
            [content[key] for key in self.NODE_CONTENT_KEYS if key in content]
        )

    def get_document_id(self):
        return "::".join(
            [
                self.tree_meta_json["tree_id"],
                self.node_meta_json["node_id"],
            ]
        )

    def get_title(self):
        return " ".join(
            [
                self.tree_meta_json["tree_name"],
                self.node_meta_json["page_title"],
            ]
        )

    def chunk_text(self, content: str):
        concat_str = self.chunker.create_concat_str(self.tree_meta_json)
        chunks, snippets = self.chunker.chunk(
            self.get_title(), content, concat_str
        )
        return chunks, snippets

    def embed(self, text_list) -> List[List[float]]:
        if not self.embedder.connected:
            self.embedder.connect()
        return self.embedder.embed(text_list)

    def prepare_additional_display_data(self):
        try:
            display = {
                "title": self.tree_meta_json["tree_name"] or "",
                "subtitle": self.node_meta_json["page_title"] or "",
            }
        except Exception:
            self._logger.warning(
                "Could not prepare additional display"
                f" data for tree {self.get_document_id()}"
            )
            return {}

        return {"display": display}

    def prepare_additional_data(self):
        other_tree_columns = [
            "org_id",
            "language",
            "tree_name",
            "tree_description",
            "tags",
            "connector_id",
            "tree_id",
            "create_date",
            "last_modified",
            "connector_id",
        ]
        other_meta_tree = {
            f"tree_{k}": v
            for k, v in self.tree_meta_json.items()
            if k not in other_tree_columns
        }
        other_meta_tree["tree_id"] = self.tree_meta_json["tree_id"]
        other_node_columns = ["page_title", "node_id"]
        other_meta_node = {
            f"node_{k}": v
            for k, v in self.node_meta_json.items()
            if k not in other_node_columns
        }
        result = other_meta_node.copy()
        result.update(other_meta_tree)
        result.update(self.prepare_additional_display_data())

        return result
