"""Alter source_id to not null in semantic_search_item table

Revision ID: 9e62d8087893
Revises: f6d776e3b65b
Create Date: 2023-08-22 17:59:47.471957

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9e62d8087893"
down_revision = "f6d776e3b65b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "semantic_search_item",
        sa.Column(
            "semantic_search_source_id",
            sa.BigInteger(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.alter_column(
        "semantic_search_item",
        sa.Column(
            "semantic_search_source_id",
            sa.BigInteger(),
            nullable=True,
        ),
    )
