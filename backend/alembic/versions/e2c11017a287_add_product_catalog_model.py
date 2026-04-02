"""add_product_catalog_model

Revision ID: e2c11017a287
Revises: 4e009d45e038
Create Date: 2026-04-02 08:17:27.272442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e2c11017a287'
down_revision: Union[str, Sequence[str], None] = '4e009d45e038'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('product_catalogs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sector_code', sa.Integer(), nullable=True),
        sa.Column('sector_name', sa.String(), nullable=True),
        sa.Column('program_code', sa.Integer(), nullable=True),
        sa.Column('program_name', sa.String(), nullable=True),
        sa.Column('product_code', sa.Integer(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('measured_through', sa.String(), nullable=True),
        sa.Column('indicator_code', sa.Integer(), nullable=True),
        sa.Column('product_indicator', sa.String(), nullable=True),
        sa.Column('measurement_unit', sa.String(), nullable=True),
        sa.Column('main_indicator', sa.String(), nullable=True),
        sa.Column('is_national', sa.String(), nullable=True),
        sa.Column('is_territorial', sa.String(), nullable=True),
        sa.Column('selected_to_project', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_catalogs_id'), 'product_catalogs', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_product_catalogs_id'), table_name='product_catalogs')
    op.drop_table('product_catalogs')
