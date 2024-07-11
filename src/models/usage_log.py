import datetime

from sqlalchemy import JSON, DateTime, Integer, Text
from sqlalchemy.orm import mapped_column

from src.core.deps.database import Base


class UsageLog(Base):
    __tablename__ = "authoring_analytics_data"

    id = mapped_column(Integer, primary_key=True)

    # Operation
    operation = mapped_column(Text, nullable=False)
    prompt = mapped_column(JSON, nullable=False)
    input = mapped_column(JSON, nullable=False)
    response = mapped_column(JSON, nullable=False)
    output = mapped_column(JSON, nullable=False)

    # Batch
    chain_id = mapped_column(Text, nullable=True)
    chain_operation = mapped_column(Text, nullable=True)

    # Audit
    user_id = mapped_column(Integer, nullable=False)
    org_id = mapped_column(Integer, nullable=False)
    project_id = mapped_column(Integer, nullable=False)
    created_at = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    updated_at = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
