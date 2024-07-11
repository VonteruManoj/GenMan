"""change date columns to nullable

Revision ID: 81fc9fda064c
Revises: 0ec823fd8ed3
Create Date: 2023-08-09 16:12:36.943319

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "81fc9fda064c"
down_revision = "0ec823fd8ed3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "semantic_search_zt_trees_item", "create_date", nullable=True
    )
    op.alter_column(
        "semantic_search_zt_trees_item", "last_opened", nullable=True
    )
    op.alter_column(
        "semantic_search_zt_trees_item", "last_modified", nullable=True
    )


def downgrade() -> None:
    # Cannot downgrade nullable columns
    pass
