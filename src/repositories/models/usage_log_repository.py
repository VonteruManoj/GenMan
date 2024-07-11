import json
import math
from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import DateTime, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, text

from src.concerns.authoring import AuthoringPromptsOperationNames
from src.models.usage_log import UsageLog
from src.repositories.audit import AuditInMemoryRepository


class UsageLogRepository:
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        audit_repository: AuditInMemoryRepository,
    ) -> None:
        self.session_factory = session_factory
        self.audit_repository = audit_repository
        self._filters = {}

    def create(
        self,
        operation: str,
        prompt: str,
        input: str,
        response: str,
        output: str,
        chain_id: str,
        chain_operation: str,
    ) -> UsageLog:
        with self.session_factory() as session:
            log = UsageLog(
                operation=operation,
                prompt=prompt,
                input=input,
                response=response,
                output=output,
                chain_id=chain_id,
                chain_operation=chain_operation,
                user_id=self.audit_repository.data.user_id,
                org_id=self.audit_repository.data.org_id,
                project_id=self.audit_repository.data.project_id,
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log

    def paginated(
        self, page: int, per_page: int, sort_by: str, sort_dir: str
    ) -> dict:
        with self.session_factory() as session:
            sort_column = getattr(UsageLog, sort_by)

            # Find chain ids
            query = session.query(
                UsageLog.chain_id.label("chain_id"),
                (
                    func.min(sort_column)
                    if sort_dir
                    else func.max(sort_column)
                ).label("sort_column"),
            )

            # Set filters [search]
            search = self.filters["search"]
            if search:
                query = query.filter(
                    or_(
                        text("input::text ilike :search_pattern"),
                        text("output::text ilike :search_pattern"),
                    ).params(search_pattern=f"%{search}%")
                )

            # Set filters [start_date]
            if self.filters["start_date"]:
                # Convert the ISO format date to a datetime object
                start_datetime = datetime.fromisoformat(
                    self.filters["start_date"]
                )

                # Query records created after the start date
                query = query.filter(
                    UsageLog.created_at >= func.cast(start_datetime, DateTime)
                )

            # Set filters [end_date]
            if self.filters["end_date"]:
                # Convert the ISO format date to a datetime object
                end_datetime = datetime.fromisoformat(self.filters["end_date"])

                # Query records created before the end date
                query = query.filter(
                    UsageLog.created_at <= func.cast(end_datetime, DateTime)
                )

            # Set filters [prompts]
            query = query.filter(
                UsageLog.chain_operation.in_(self.filters["prompts"])
            )

            # Set filters [org_id]
            if self.filters["org_id"]:
                query = query.filter(UsageLog.org_id == self.filters["org_id"])

            # Set filters [failed]
            if self.filters["failed"] is not None:
                expect = (
                    json.dumps(True)
                    if self.filters["failed"] is True
                    else json.dumps(False)
                )

                subquery = (
                    session.query(UsageLog.chain_id)
                    .filter(
                        UsageLog.operation == "moderation",
                        text("output::text like :output_search_pattern"),
                    )
                    .params(output_search_pattern=f'"{expect}"')
                    .subquery()
                )

                query = query.filter(UsageLog.chain_id.in_(subquery))

            # Sorting
            query = query.order_by(
                text("sort_column")
                if sort_dir == "asc"
                else text("sort_column DESC")
            )

            # Group by chain_id
            query = query.group_by(UsageLog.chain_id)

            # Get total count
            total_count = query.count()

            # Paginate
            query = query.limit(per_page).offset((page - 1) * per_page)

            query = query.subquery()

            # Set select query
            records_query = session.query(UsageLog).where(
                UsageLog.chain_id.in_(select(query.c.chain_id))
            )
            # .order_by(
            #     sort_column.desc()
            #     if sort_dir == "asc"
            #     else sort_column
            # )

            # Get records
            records = records_query.all()

        # Group records
        grouped_records = {}
        for record in records:
            if record.chain_id not in grouped_records:
                grouped_records[record.chain_id] = []

            grouped_records[record.chain_id].append(record)

        records = []
        for chain_id, chain_records in grouped_records.items():
            links = [
                {
                    "id": int(r.id),
                    "operation": str(r.operation),
                    "prompt": r.prompt,
                    "input": r.input,
                    "response": r.response,
                    "output": r.output,
                    "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for r in chain_records
            ]

            records.append(
                {
                    "chain_id": chain_id,
                    "chain_operation": chain_records[0].chain_operation,
                    "user_id": chain_records[0].user_id,
                    "org_id": chain_records[0].org_id,
                    "project_id": chain_records[0].project_id,
                    "chain_links": links,
                    "created_at": min([r["created_at"] for r in links]),
                }
            )

        # Sort grouped records by the given column
        records.sort(
            key=lambda x: x[sort_by],
            reverse=True if sort_dir == "desc" else False,
        )

        # since "from" its a reserved keyword in python,
        # we use a JSON object
        meta = {
            "current_page": page,
            "from": per_page * (page - 1) + 1,
            "to": per_page * (page - 1) + len(records),
            "per_page": per_page,
            "total": total_count,
            "last_page": math.ceil(total_count / per_page),
        }

        return {
            "records": records,
            "meta": meta,
        }

    @property
    def filters(self) -> dict:
        return self._filters

    @filters.setter
    def filters(self, filters: str) -> None:
        self._filters = filters

        # if no filters are
        if not filters.get("prompts"):
            self._filters["prompts"] = AuthoringPromptsOperationNames.list()
