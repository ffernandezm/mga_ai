"""Add optional territorial level to localization records.

Revision ID: a1c6d2e8f903
Revises: f2a4c9d8e701
"""

from alembic import op
import sqlalchemy as sa

revision = "a1c6d2e8f903"
down_revision = "f2a4c9d8e701"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("localization", sa.Column("administrative_level", sa.Text(), nullable=True, server_default="municipal"))


def downgrade():
    op.drop_column("localization", "administrative_level")