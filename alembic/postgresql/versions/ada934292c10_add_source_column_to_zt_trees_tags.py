"""Add source column to semantic_search_zt_trees_item_tag table

Revision ID: ada934292c10
Revises: 81fc9fda064c
Create Date: 2023-08-14 17:55:47.330663

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ada934292c10"
down_revision = "81fc9fda064c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "semantic_search_zt_trees_item_tag",
        sa.Column(
            "source",
            sa.SmallInteger(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("semantic_search_zt_trees_item_tag", "source")
