"""Init semantic search schemas

Revision ID: 2642b78cb5da
Revises:
Create Date: 2023-06-20 19:45:23.095318

"""

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.orm import Session

from alembic import op

# revision identifiers, used by Alembic.
revision = "2642b78cb5da"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "semantic_search_item",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("embeddings", sa.ARRAY(sa.Float()), nullable=False),
        sa.Column("org_id", sa.Integer, nullable=False),
        sa.Column("language", sa.Text, nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("snippet", sa.Text, nullable=False),
        sa.Column(
            "source_type",
            sa.Enum("zt_trees", name="semantic_search_source"),
            nullable=False,
        ),
        sa.Column(
            "semantic_search_parent_item_id", sa.Integer, nullable=False
        ),
    )
    op.execute(
        "ALTER TABLE semantic_search_item"
        " ALTER COLUMN embeddings TYPE VECTOR(768)"
    )

    op.create_table(
        "semantic_search_zt_trees_item",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("node_id", sa.Integer, nullable=False),
        sa.Column("tree_name", sa.Text, nullable=False),
        sa.Column("tree_description", sa.Text, nullable=False),
        sa.Column("tree_id", sa.Integer, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False),
        sa.Column("create_date", sa.DateTime, nullable=False),
        sa.Column("last_opened", sa.DateTime, nullable=False),
        sa.Column("last_modified", sa.DateTime, nullable=False),
        sa.Column("is_private", sa.Boolean, nullable=False),
        sa.Column("page_title", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
    )

    op.create_table(
        "semantic_search_zt_trees_item_keyword",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "semantic_search_zt_trees_item_id", sa.Integer, nullable=True
        ),
        sa.Column("keyword", sa.Text, nullable=True),
    )
    op.create_foreign_key(
        "fk_ssztik_sszti_semantic_search_zt_trees_item_id",
        "semantic_search_zt_trees_item_keyword",
        "semantic_search_zt_trees_item",
        ["semantic_search_zt_trees_item_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_table(
        "semantic_search_zt_trees_item_tag",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "semantic_search_zt_trees_item_id", sa.Integer, nullable=True
        ),
        sa.Column("tag", sa.Text, nullable=True),
    )
    op.create_foreign_key(
        "fk_ssztit_sszti_semantic_search_zt_trees_item_id",
        "semantic_search_zt_trees_item_tag",
        "semantic_search_zt_trees_item",
        ["semantic_search_zt_trees_item_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_ssztik_sszti_semantic_search_zt_trees_item_id",
        "semantic_search_zt_trees_item_keyword",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ssztit_sszti_semantic_search_zt_trees_item_id",
        "semantic_search_zt_trees_item_tag",
        type_="foreignkey",
    )

    op.drop_table("semantic_search_item")
    op.drop_table("semantic_search_zt_trees_item")
    op.drop_table("semantic_search_zt_trees_item_keyword")
    op.drop_table("semantic_search_zt_trees_item_tag")
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text("DROP TYPE semantic_search_source"))
