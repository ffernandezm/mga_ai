"""Make survey unique per project

Revision ID: 8b1d2e3f4a5b
Revises: 6f4d8b2a1c30
Create Date: 2026-09-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8b1d2e3f4a5b'
down_revision: Union[str, Sequence[str], None] = '6f4d8b2a1c30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('survey', sa.Column('comment', sa.Text(), nullable=True))
    op.execute(
        sa.text(
            'DELETE FROM survey '
            'WHERE id NOT IN ('
            'SELECT MAX(id) FROM survey GROUP BY project_id'
            ')'
        )
    )
    op.create_unique_constraint('uq_survey_project_id', 'survey', ['project_id'])


def downgrade() -> None:
    op.drop_constraint('uq_survey_project_id', 'survey', type_='unique')
    op.drop_column('survey', 'comment')