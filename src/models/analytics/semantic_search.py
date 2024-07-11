import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.deps.database import MySQLBase


class SemanticSearchAnalytic(MySQLBase):
    __tablename__ = "semantic_search_sessions"

    # Batch data
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    operation: Mapped[str] = mapped_column(Text, nullable=False)
    deployment_id: Mapped[str] = mapped_column(Text, nullable=False)
    current_deployment_type: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(Text, nullable=True)
    previous_session_id: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    # Audit data
    causer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    causer_type: Mapped[str] = mapped_column(Text, nullable=False)
    org_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Events
    events = relationship(
        "SemanticSearchAnalyticEvent", lazy="selectin", back_populates="batch"
    )


class SemanticSearchAnalyticEvent(MySQLBase):
    __tablename__ = "semantic_search_sessions_event"

    # Event data
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    # Analytics data
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data: Mapped[Optional[dict | list]] = mapped_column(JSON, nullable=True)

    # Foreign key to batch
    semantic_search_sessions_id: Mapped[String(36)] = mapped_column(
        String(36),
        ForeignKey("semantic_search_sessions.id"),
        nullable=False,
    )

    batch = relationship("SemanticSearchAnalytic", back_populates="events")
