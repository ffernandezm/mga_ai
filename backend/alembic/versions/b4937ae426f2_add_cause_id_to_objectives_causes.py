"""add_cause_id_to_objectives_causes

Revision ID: b4937ae426f2
Revises: 1920681f8f02
Create Date: 2026-03-05 22:28:28.140556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4937ae426f2'
down_revision: Union[str, Sequence[str], None] = '1920681f8f02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add cause_id column to objectives_causes table
    op.add_column('objectives_causes', sa.Column('cause_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove cause_id column from objectives_causes table
    op.drop_column('objectives_causes', 'cause_id')
