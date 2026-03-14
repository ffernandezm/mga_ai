"""Add description field to products and activities

Revision ID: 1920681f8f02
Revises: 7dd606c89796
Create Date: 2026-03-05 19:59:59.800110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1920681f8f02'
down_revision: Union[str, Sequence[str], None] = '7dd606c89796'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add description column to products table
    op.add_column('products', sa.Column('description', sa.Text(), nullable=True))
    
    # Add description column to activities table
    op.add_column('activities', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop description column from activities table
    op.drop_column('activities', 'description')
    
    # Drop description column from products table
    op.drop_column('products', 'description')
