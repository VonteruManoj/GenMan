"""Create semantic search sources table

Revision ID: c640fc4b7721
Revises: ada934292c10
Create Date: 2023-08-22 17:41:54.173440

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "c640fc4b7721"
down_revision = "ada934292c10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "semantic_search_sources",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "source_type",
            # NOTE: same ENUM used in the semantic_search_item table
            postgresql.ENUM(name="semantic_search_source", create_type=False),
            nullable=False,
        ),
        sa.Column("org_id", sa.Integer, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("semantic_search_sources")
