"""Create semantic search analytics tables

Revision ID: a9617e25884f
Revises:
Create Date: 2023-12-27 12:57:09.775352

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a9617e25884f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "semantic_search_sessions",
        # Operations batch
        sa.Column(
            "id",
            sa.CHAR(length=36),
            nullable=False,
            primary_key=True,
        ),
        # other columns
        sa.Column("operation", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        # Log data
        sa.Column("deployment_id", sa.Text, nullable=False),
        sa.Column("current_deployment_type", sa.Text, nullable=True),
        sa.Column("location", sa.Text, nullable=True),
        sa.Column("previous_session_id", sa.Text, nullable=True),
        # Audit data
        sa.Column("causer_id", sa.Integer, nullable=True),
        sa.Column("causer_type", sa.Text, nullable=True),
        sa.Column("org_id", sa.Integer, nullable=True),
    )

    op.create_table(
        "semantic_search_sessions_event",
        # Operation data
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("operation", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        # Log data
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("data", sa.JSON, nullable=True),
        # Foreign key to batch
        sa.Column(
            "semantic_search_sessions_id",
            sa.CHAR(length=36),
            sa.ForeignKey("semantic_search_sessions.id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("semantic_search_sessions_event")
    op.drop_table("semantic_search_sessions")
