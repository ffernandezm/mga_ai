"""Add value_chain_objective_id to objectives_causes

Revision ID: 972d057eee35
Revises: 38b28cf30287
Create Date: 2026-03-06 07:33:12.503526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '972d057eee35'
down_revision: Union[str, Sequence[str], None] = '38b28cf30287'
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
