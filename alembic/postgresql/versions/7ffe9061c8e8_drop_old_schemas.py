"""drop old schemas

Revision ID: 7ffe9061c8e8
Revises: b7b93f5cce68
Create Date: 2023-09-15 19:14:52.804097

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7ffe9061c8e8"
down_revision = "b7b93f5cce68"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    op.drop_constraint(
        "fk_ssi_sss_semantic_search_source_id",
        "semantic_search_item",
        type_="foreignkey",
    )

    op.drop_table("semantic_search_html_item")
    op.drop_table("semantic_search_item")
    op.drop_table("semantic_search_sources")
    op.drop_table("semantic_search_zt_trees_item")
    op.drop_table("semantic_search_zt_trees_item_keyword")
    op.drop_table("semantic_search_zt_trees_item_tag")


def downgrade() -> None:
    pass
