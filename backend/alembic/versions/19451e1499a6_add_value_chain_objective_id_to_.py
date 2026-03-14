"""Add value_chain_objective_id to objectives_causes

Revision ID: 19451e1499a6
Revises: b4937ae426f2
Create Date: 2026-03-06 07:33:59.393449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19451e1499a6'
down_revision: Union[str, Sequence[str], None] = 'b4937ae426f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('objectives_causes', sa.Column('value_chain_objective_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'objectives_causes', 'value_chain_objectives', ['value_chain_objective_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'objectives_causes', type_='foreignkey')
    op.drop_column('objectives_causes', 'value_chain_objective_id')
