"""add html item table

Revision ID: b7b93f5cce68
Revises: 9e62d8087893
Create Date: 2023-08-22 18:08:22.035165

"""

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.orm import Session

from alembic import op

# from src.models.semantic_search_item import SemanticSearchHtmlItem

# revision identifiers, used by Alembic.
revision = "b7b93f5cce68"
down_revision = "9e62d8087893"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "semantic_search_html_item",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("html_id", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("type", sa.Text, nullable=False),
    )
    op.alter_column(
        "semantic_search_item",
        "source_type",
        type_=sa.SmallInteger(),
        postgresql_using="(CASE source_type WHEN 'zt_trees' THEN 1 END)",
    )
    op.alter_column(
        "semantic_search_sources",
        "source_type",
        type_=sa.SmallInteger(),
        postgresql_using="(CASE source_type WHEN 'zt_trees' THEN 1 END)",
    )
    bind = op.get_bind()
    session = Session(bind=bind)
    session.execute(text("DROP TYPE semantic_search_source"))
    session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    # rows = session.query(SemanticSearchHtmlItem).count()
    # if rows:
    #     raise ValueError(
    #         "There are still html items in the database, please remove them "
    #         "before downgrading"
    #     )
    session.close()
    op.drop_table("semantic_search_html_item")
    source_type = sa.Enum("zt_trees", name="semantic_search_source")
    source_type.create(op.get_bind())
    op.alter_column(
        "semantic_search_item",
        "source_type",
        type_=source_type,
        postgresql_using="(CASE source_type WHEN 1 THEN 'zt_trees'::"
        "semantic_search_source END)",
    )
    op.alter_column(
        "semantic_search_sources",
        "source_type",
        type_=source_type,
        postgresql_using="(CASE source_type WHEN 1 THEN 'zt_trees'::"
        "semantic_search_source END)",
    )
