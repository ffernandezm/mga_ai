"""add chat metadata columns

Revision ID: c4a9d7e91b23
Revises: 9d4e8b2c1f07
Create Date: 2026-09-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4a9d7e91b23"
down_revision = "c4e8f5a7b206"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("chat_history", sa.Column("trace_payload", sa.Text(), nullable=True))
    op.add_column("chat_history", sa.Column("suggested_changes_payload", sa.Text(), nullable=True))
    op.add_column("chat_history", sa.Column("generation_status", sa.String(), nullable=True))
    op.add_column("chat_history", sa.Column("error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("chat_history", "error")
    op.drop_column("chat_history", "generation_status")
    op.drop_column("chat_history", "suggested_changes_payload")
    op.drop_column("chat_history", "trace_payload")