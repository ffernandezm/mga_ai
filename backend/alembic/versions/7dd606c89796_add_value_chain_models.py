"""Add value chain models

Revision ID: 7dd606c89796
Revises: ffe44517c125
Create Date: 2026-03-05 16:23:43.689501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '7dd606c89796'
down_revision: Union[str, Sequence[str], None] = 'ffe44517c125'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'value_chains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_value_chains_id'), 'value_chains', ['id'], unique=False)
    op.create_index(op.f('ix_value_chains_name'), 'value_chains', ['name'], unique=False)

    op.create_table(
        'value_chain_objectives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('value_chain_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['value_chain_id'], ['value_chains.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_value_chain_objectives_id'), 'value_chain_objectives', ['id'], unique=False)
    op.create_index(op.f('ix_value_chain_objectives_name'), 'value_chain_objectives', ['name'], unique=False)

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('value_chain_objective_id', sa.Integer(), nullable=False),
        sa.Column('measured_through', sa.String(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('stage', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['value_chain_objective_id'], ['value_chain_objectives.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)

    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('stage', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_activities_id'), 'activities', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_activities_id'), table_name='activities')
    op.drop_table('activities')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_value_chain_objectives_name'), table_name='value_chain_objectives')
    op.drop_index(op.f('ix_value_chain_objectives_id'), table_name='value_chain_objectives')
    op.drop_table('value_chain_objectives')
    op.drop_index(op.f('ix_value_chains_name'), table_name='value_chains')
    op.drop_index(op.f('ix_value_chains_id'), table_name='value_chains')
    op.drop_table('value_chains')
