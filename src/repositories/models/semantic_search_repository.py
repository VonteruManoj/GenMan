from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from src.api.v1.endpoints.requests.semantic_search import SearchFilters
from src.builders.queries.semantic_search import (
    SemanticSearchDeployDocumentsCountBuilder,
    SemanticSearchSearchQueryBuilder,
    SemanticSearchSearchSuggestionsQueryBuilder,
)
from src.core.config import get_settings
from src.models.semantic_search_item import (
    SemanticSearchDocument,
    SemanticSearchItem,
)


class SemanticSearchRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        self.session_factory = session_factory

    def create_document(
        self,
        org_id: int,
        language: str,
        title: str,
        description: str,
        tags: list[str],
        data: dict,
        connector_id: int,
        document_id: str,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> SemanticSearchDocument:
        document = SemanticSearchDocument(
            org_id=org_id,
            language=language,
            title=title,
            description=description,
            tags=tags,
            data=data,
            connector_id=connector_id,
            document_id=document_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        with self.session_factory() as session:
            session.add(document)
            session.commit()
            session.refresh(document)

        return document

    def create_item(
        self,
        embeddings: list[float],
        chunk: str,
        snippet: str,
        document: SemanticSearchDocument,
    ) -> SemanticSearchItem:
        item = SemanticSearchItem(
            embeddings=embeddings,
            chunk=chunk,
            snippet=snippet,
            document_id=document.id,
        )
        item.document = document

        with self.session_factory() as session:
            session.add(item)
            session.commit()
            session.refresh(item)

        return item

    def search(
        self,
        embeddings: list[float],
        org_id: int,
        filters: SearchFilters,
        limit: int | None,
    ) -> (SemanticSearchItem, float):
        builder = SemanticSearchSearchQueryBuilder(
            embeddings, org_id, get_settings().SEMANTIC_SEARCH_THRESHOLD
        )
        builder.filters = filters
        builder.limit = limit
        query = builder.build()

        with self.session_factory() as session:
            results = session.execute(query).fetchall()
        return [r[0] for r in results], [r[1] for r in results]

    def find_document(self, document_id: str, connector_id: int, org_id: int):
        with self.session_factory() as session:
            document_item = session.scalars(
                select(SemanticSearchDocument).where(
                    SemanticSearchDocument.document_id == document_id,
                    SemanticSearchDocument.connector_id == connector_id,
                    SemanticSearchDocument.org_id == org_id,
                )
            ).first()
        return document_item

    def search_best(
        self,
        embeddings: list[float],
        org_id: int,
        filters: SearchFilters,
        n: int = 5,
    ) -> dict:
        builder = SemanticSearchSearchQueryBuilder(
            embeddings, org_id, get_settings().SEMANTIC_SEARCH_THRESHOLD
        )
        builder.filters = filters
        builder.limit = n
        query = builder.build_best()

        with self.session_factory() as session:
            results = session.scalars(query).fetchall()
        return results

    def remove_item(self, document_id: str, org_id: int):
        with self.session_factory() as session:
            records = session.execute(
                select(SemanticSearchItem.id, SemanticSearchDocument.id)
                .join(
                    SemanticSearchDocument,
                    SemanticSearchItem.document_id
                    == SemanticSearchDocument.id,
                )
                .where(SemanticSearchDocument.document_id == document_id)
                .where(SemanticSearchDocument.org_id == org_id)
            ).fetchall()
            semantic_search_item_ids = [r[0] for r in records]
            semantic_search_document_ids = [r[1] for r in records]

            semantic_search_item_dq = delete(SemanticSearchItem).where(
                SemanticSearchItem.id.in_(semantic_search_item_ids)
            )
            semantic_search_document_dq = delete(SemanticSearchDocument).where(
                SemanticSearchDocument.id.in_(semantic_search_document_ids)
            )

            session.execute(semantic_search_item_dq)
            session.execute(semantic_search_document_dq)
            session.commit()
            return semantic_search_item_ids

    def remove_items_like(self, like_document_id: str, org_id: int):
        with self.session_factory() as session:
            records = session.execute(
                select(SemanticSearchDocument.id)
                .where(
                    SemanticSearchDocument.document_id.like(like_document_id)
                )
                .where(SemanticSearchDocument.org_id == org_id)
            ).fetchall()
            semantic_search_document_ids = [r[0] for r in records]

            semantic_search_item_dq = (
                delete(SemanticSearchItem)
                .where(
                    SemanticSearchItem.document_id.in_(
                        semantic_search_document_ids
                    )
                )
                .returning(SemanticSearchItem.id)
            )
            semantic_search_document_dq = delete(SemanticSearchDocument).where(
                SemanticSearchDocument.id.in_(semantic_search_document_ids)
            )

            semantic_search_item_ids = session.scalars(
                semantic_search_item_dq
            ).fetchall()
            session.execute(semantic_search_document_dq)
            session.commit()
            return semantic_search_item_ids

    def get_search_suggestions(
        self,
        search: str,
        org_id: int,
        filters: SearchFilters,
        limit: int | None,
    ) -> list[str]:
        builder = SemanticSearchSearchSuggestionsQueryBuilder(org_id)
        builder.limit = limit
        builder.filters = filters
        query = builder.build(search)

        with self.session_factory() as session:
            results = session.scalars(query).fetchall()

        return results

    def get_tags(
        self,
        org_id: int,
    ) -> list[str]:
        query = (
            select(func.unnest(SemanticSearchDocument.tags))
            .filter(SemanticSearchDocument.org_id == org_id)
            .distinct()
        )

        with self.session_factory() as session:
            tags = session.scalars(query).fetchall()

        return tags

    def get_tags_with_meta(self, org_id: int) -> list[str]:
        with self.session_factory() as session:
            subquery = (
                session.query(
                    SemanticSearchDocument.connector_id,
                    func.unnest(SemanticSearchDocument.tags).label("tag"),
                )
                .where(SemanticSearchDocument.org_id == org_id)
                .subquery()
            )
            return (
                session.query(
                    subquery.c.tag,
                    subquery.c.connector_id,
                    func.count().label("count"),
                )
                .group_by(subquery.c.tag, subquery.c.connector_id)
                .all()
            )

    def find_semantic_search_item_by_id(
        self,
        item_id: int,
        org_id: int,
    ) -> SemanticSearchItem | None:
        with self.session_factory() as session:
            return session.scalars(
                select(SemanticSearchItem)
                .filter(SemanticSearchItem.id == item_id)
                .where(SemanticSearchDocument.org_id == org_id)
            ).first()

    def find_semantic_search_items_by_ids(
        self,
        items_ids: list[int],
        org_id: int,
    ) -> list[SemanticSearchItem]:
        with self.session_factory() as session:
            return session.scalars(
                select(SemanticSearchItem)
                .join(
                    SemanticSearchDocument,
                    SemanticSearchItem.document_id
                    == SemanticSearchDocument.id,
                )
                .filter(SemanticSearchItem.id.in_(items_ids))
                .where(SemanticSearchDocument.org_id == org_id)
            ).fetchall()

    def get_documents(
        self,
        org_id: int | None,
        connector_id: int | None,
        limit: int | None,
        offset: int | None,
    ) -> list[dict]:
        query = select(SemanticSearchDocument)

        if org_id is None and connector_id is None:
            raise ValueError("org_id or connector_id must be provided")

        if (limit is None and offset is not None) or (
            limit is not None and offset is None
        ):
            raise ValueError("limit and offset must be provided together")

        if org_id:
            query = query.filter(SemanticSearchDocument.org_id == org_id)

        if connector_id:
            query = query.filter(
                SemanticSearchDocument.connector_id == connector_id
            )

        if limit is not None and offset is not None:
            query = query.limit(limit).offset(offset)

        query = query.order_by(SemanticSearchDocument.id)

        with self.session_factory() as session:
            return session.scalars(query).fetchall()

    def get_languages(self, org_id: int) -> list[str]:
        query = (
            select(SemanticSearchDocument.language)
            .filter(SemanticSearchDocument.org_id == org_id)
            .distinct()
        )

        with self.session_factory() as session:
            return session.scalars(query).fetchall()

    def deployment_has_documents(
        self,
        org_id: int,
        filters: SearchFilters,
    ) -> bool:
        builder = SemanticSearchDeployDocumentsCountBuilder(org_id)
        builder.filters = filters
        query = builder.build()

        with self.session_factory() as session:
            results = session.scalars(query).fetchall()

        return len(results) > 0
