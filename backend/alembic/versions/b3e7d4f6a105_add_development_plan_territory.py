"""Add territorial scope fields to development plans.

Revision ID: b3e7d4f6a105
Revises: a1c6d2e8f903
"""

from alembic import op
import sqlalchemy as sa

revision = "b3e7d4f6a105"
down_revision = "a1c6d2e8f903"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("development_plans", sa.Column("territorial_level", sa.String(), nullable=True))
    op.add_column("development_plans", sa.Column("department", sa.String(), nullable=True))
    op.add_column("development_plans", sa.Column("municipality", sa.String(), nullable=True))


def downgrade():
    op.drop_column("development_plans", "municipality")
    op.drop_column("development_plans", "department")
    op.drop_column("development_plans", "territorial_level")