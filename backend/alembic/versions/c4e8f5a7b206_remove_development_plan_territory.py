"""Remove territorial fields from development plans.

Revision ID: c4e8f5a7b206
Revises: b3e7d4f6a105
"""

from alembic import op
import sqlalchemy as sa

revision = "c4e8f5a7b206"
down_revision = "b3e7d4f6a105"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("development_plans", "municipality")
    op.drop_column("development_plans", "department")
    op.drop_column("development_plans", "territorial_level")


def downgrade():
    op.add_column("development_plans", sa.Column("territorial_level", sa.String(), nullable=True))
    op.add_column("development_plans", sa.Column("department", sa.String(), nullable=True))
    op.add_column("development_plans", sa.Column("municipality", sa.String(), nullable=True))