"""add chat_history to problems

Revision ID: 422737255143
Revises: 
Create Date: 2025-09-11 11:33:20.619999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '422737255143'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("problems", sa.Column("chat_history", sa.JSON, nullable=True))

def downgrade():
    op.drop_column("problems", "chat_history")
