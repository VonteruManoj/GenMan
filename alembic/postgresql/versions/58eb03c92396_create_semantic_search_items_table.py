"""create semantic search items table

Revision ID: 58eb03c92396
Revises: 5a805796c8cb
Create Date: 2023-09-15 19:24:49.884050

"""

import os

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "58eb03c92396"
down_revision = "5a805796c8cb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    embeddings_size = int(
        os.environ.get("EMBEDDINGS_DIMENSIONS", "4096").strip("\"'")
    )

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "semantic_search_items",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("embeddings", sa.ARRAY(sa.Float()), nullable=False),
        sa.Column("chunk", sa.Text, nullable=False),
        sa.Column("snippet", sa.Text, nullable=False),
        sa.Column("document_id", sa.Integer, nullable=False),
    )
    op.execute(
        "ALTER TABLE semantic_search_items"
        f" ALTER COLUMN embeddings TYPE VECTOR({embeddings_size})"
    )

    op.create_foreign_key(
        "fk_ssi_ssd_document_id",
        "semantic_search_items",
        "semantic_search_documents",
        ["document_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ssi_ssd_document_id",
        "semantic_search_items",
        type_="foreignkey",
    )

    op.drop_table("semantic_search_items")
