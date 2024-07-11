import datetime
import json

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.config import get_settings
from src.core.deps.database import Base
from src.util.tags_parser import TagParser

settings = get_settings()


class SemanticSearchDocument(Base):
    __tablename__ = "semantic_search_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=[]
    )
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    connector_id: Mapped[int] = mapped_column(Integer, nullable=False)
    document_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=datetime.datetime.utcnow
    )
    items: Mapped[list["SemanticSearchItem"]] = relationship(
        back_populates="document"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "orgId": self.org_id,
            "language": self.language,
            "title": self.title,
            "description": self.description,
            "tags": TagParser.from_str(self.tags).tags,
            "data": (
                json.loads(self.data)
                if isinstance(self.data, str)
                else self.data
            ),
            "connectorId": self.connector_id,
            "articleId": self.document_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }

    def to_analytics_dict(self):
        return {
            "id": self.id,
            "connectorId": self.connector_id,
            "documentId": self.document_id,
            "title": self.title,
        }

    def sorting_values(self) -> list[any]:
        values = [self.title]

        if "node_id" in self.data:
            values.append(self.data["node_id"])

        return values


class SemanticSearchItem(Base):
    __tablename__ = "semantic_search_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    embeddings = mapped_column(
        Vector(settings.EMBEDDINGS_DIMENSIONS), nullable=False
    )
    chunk: Mapped[str] = mapped_column(
        String, nullable=False
    )  # text + context
    snippet: Mapped[str] = mapped_column(String, nullable=False)  # text
    document_id: Mapped[int] = mapped_column(
        ForeignKey("semantic_search_documents.id"),
        nullable=False,
    )
    document: Mapped["SemanticSearchDocument"] = relationship(
        back_populates="items",
        lazy="selectin",
        uselist=False,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "snippet": self.snippet,
            "document": self.document.to_dict(),
        }

    def to_analytics_dict(self):
        return {
            "id": self.id,
            "snippet": self.snippet,
            "document": self.document.to_analytics_dict(),
        }
