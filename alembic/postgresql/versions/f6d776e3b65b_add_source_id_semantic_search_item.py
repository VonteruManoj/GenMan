"""Add source ref. in sematic search item table

Revision ID: f6d776e3b65b
Revises: c640fc4b7721
Create Date: 2023-08-22 17:52:30.093704

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f6d776e3b65b"
down_revision = "c640fc4b7721"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "semantic_search_item",
        sa.Column(
            "semantic_search_source_id",
            sa.BigInteger(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_ssi_sss_semantic_search_source_id",
        "semantic_search_item",
        "semantic_search_sources",
        ["semantic_search_source_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ssi_sss_semantic_search_source_id",
        "semantic_search_item",
        type_="foreignkey",
    )

    op.drop_column("semantic_search_item", "semantic_search_source_id")
