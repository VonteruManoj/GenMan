"""Create semantic search analytics table

Revision ID: 0ec823fd8ed3
Revises: 9e76f5f7c782
Create Date: 2023-08-02 14:48:40.885831

"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "0ec823fd8ed3"
down_revision = "9e76f5f7c782"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "semantic_search_analytics",
        # Operations batch
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("operation", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        # Audit data
        sa.Column("causer_id", sa.Integer, nullable=False),
        sa.Column("causer_type", sa.Text, nullable=False),
        sa.Column("org_id", sa.Integer, nullable=True),
    )

    op.create_table(
        "semantic_search_analytics_event",
        # Operation data
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("operation", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        # Log data
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("data", sa.JSON, nullable=True),
        # Foreign key to batch
        sa.Column(
            "semantic_search_analytics_id",
            UUID(as_uuid=True),
            sa.ForeignKey("semantic_search_analytics.id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("semantic_search_analytics_event")
    op.drop_table("semantic_search_analytics")
