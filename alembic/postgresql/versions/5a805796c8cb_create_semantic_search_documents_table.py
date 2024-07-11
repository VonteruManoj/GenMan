"""create semantic search documents table

Revision ID: 5a805796c8cb
Revises: 7ffe9061c8e8
Create Date: 2023-09-15 19:21:00.224361

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5a805796c8cb"
down_revision = "7ffe9061c8e8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "semantic_search_documents",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("org_id", sa.Integer, nullable=False),
        sa.Column("language", sa.Text, nullable=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tags", sa.ARRAY(sa.Text), nullable=False),
        sa.Column("data", sa.JSON, nullable=False),
        sa.Column("connector_id", sa.Integer, nullable=False),
        sa.Column("document_id", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("semantic_search_documents")
