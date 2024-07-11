from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.core.deps.logger import with_logger
from src.models.analytics.semantic_search import (
    SemanticSearchAnalytic,
    SemanticSearchAnalyticEvent,
)
from src.models.semantic_search_item import SemanticSearchItem
from src.repositories.audit import AuditInMemoryRepository


@with_logger()
class SemanticSearchAnalyticsRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        audit_repository: AuditInMemoryRepository,
    ) -> None:
        self.session_factory = session_factory
        self.audit_repository = audit_repository

    def find_batch_by_id(
        self,
        id: str,
    ) -> SemanticSearchAnalytic | None:
        try:
            with self.session_factory() as session:
                self._logger.debug(
                    f"Finding batch by filters: {id},"
                    f"{self.audit_repository.data.causer_id},"
                    f"{self.audit_repository.data.causer_type}"
                )
                return (
                    session.query(SemanticSearchAnalytic)
                    .filter(SemanticSearchAnalytic.id == id)
                    .filter(
                        SemanticSearchAnalytic.causer_id
                        == self.audit_repository.data.causer_id
                    )
                    .filter(
                        SemanticSearchAnalytic.causer_type
                        == self.audit_repository.data.causer_type
                    )
                    .first()
                )
        except Exception:
            return None

    def create_batch(
        self,
        operation: str,
        deployment_id: str,
    ) -> SemanticSearchAnalytic:
        semantic_search_analytic_data = SemanticSearchAnalytic(
            operation=operation,
            causer_id=self.audit_repository.data.causer_id,
            causer_type=self.audit_repository.data.causer_type,
            org_id=self.audit_repository.data.org_id,
            deployment_id=deployment_id,
        )
        with self.session_factory() as session:
            session.add(semantic_search_analytic_data)
            session.commit()
            session.refresh(semantic_search_analytic_data)

        return semantic_search_analytic_data

    def update_batch(
        self,
        batch: SemanticSearchAnalytic,
        current_deployment_type: str,
        location: str,
        previous_session_id: str,
    ) -> SemanticSearchAnalyticEvent:
        with self.session_factory() as session:
            session.add(batch)
            batch.current_deployment_type = current_deployment_type
            batch.location = location
            batch.previous_session_id = previous_session_id
            session.commit()
            session.refresh(batch)

        return batch

    def append_event_to_batch(
        self,
        batch: SemanticSearchAnalytic,
        operation: str,
        message: str | None = None,
        data: dict | None = None,
    ) -> SemanticSearchAnalyticEvent:
        semantic_search_analytic_data_event = SemanticSearchAnalyticEvent(
            operation=operation,
            message=message,
            data=data,
            semantic_search_sessions_id=batch.id,
        )

        with self.session_factory() as session:
            session.add(semantic_search_analytic_data_event)
            session.commit()
            session.refresh(semantic_search_analytic_data_event)

        return semantic_search_analytic_data_event

    def from_search(
        self,
        search: str,
        filters: dict,
        limit: int,
        sort_by: str,
        options: list[SemanticSearchItem],
        distances: list[float],
        deployment_id: str,
    ) -> SemanticSearchAnalytic:
        batch = self.create_batch(
            operation="search", deployment_id=deployment_id
        )

        items = []
        for index in range(len(options)):
            items.append(
                {
                    **(options[index].to_analytics_dict()),
                    "distance": distances[index],
                }
            )

        self.append_event_to_batch(
            batch=batch,
            operation="search",
            message=f"Found {len(items)} options for {search}",
            data={
                "request": {
                    "query": search,
                    "limit": limit,
                    "sort_by": sort_by,
                    "filters": filters,
                },
                "options": items,
            },
        )

        with self.session_factory() as session:
            session.add(batch)
            session.refresh(batch)

        return batch
