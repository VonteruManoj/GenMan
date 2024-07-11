"""create authoring analytics data table

Revision ID: 9e76f5f7c782
Revises: 2642b78cb5da
Create Date: 2023-08-01 15:50:39.324239

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "9e76f5f7c782"
down_revision = "2642b78cb5da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authoring_analytics_data",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("chain_id", sa.String(128), nullable=True),
        sa.Column("chain_operation", sa.String(64), nullable=True),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("prompt", sa.JSON, nullable=False),
        sa.Column("input", sa.JSON, nullable=False),
        sa.Column("response", sa.JSON, nullable=False),
        sa.Column("output", sa.JSON, nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("org_id", sa.Integer, nullable=False),
        sa.Column("project_id", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("authoring_analytics_data")
