"""adopt omitted MGA tables

Revision ID: 6f4d8b2a1c30
Revises: c19a024610f3
Create Date: 2026-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6f4d8b2a1c30'
down_revision: Union[str, Sequence[str], None] = 'c19a024610f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table_name: str) -> set[str]:
    return {
        column['name']
        for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _index_names(table_name: str) -> set[str]:
    return {
        index['name']
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }


def upgrade() -> None:
    """Bring tables previously hidden by create_all under Alembic ownership."""
    tables = _table_names()

    if 'chat_history' not in tables:
        op.create_table(
            'chat_history',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('tab', sa.String(), nullable=False),
            sa.Column('session_id', sa.String(), nullable=False),
            sa.Column('sender', sa.String(), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
            sa.PrimaryKeyConstraint('id'),
        )
    chat_indexes = _index_names('chat_history')
    if 'ix_chat_history_id' not in chat_indexes:
        op.create_index('ix_chat_history_id', 'chat_history', ['id'], unique=False)
    if 'ix_chat_history_session_id' not in chat_indexes:
        op.create_index('ix_chat_history_session_id', 'chat_history', ['session_id'], unique=False)

    if 'survey' not in tables:
        op.create_table(
            'survey',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('survey_json', sa.JSON(), nullable=False),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
            sa.PrimaryKeyConstraint('id'),
        )
    if 'ix_survey_id' not in _index_names('survey'):
        op.create_index('ix_survey_id', 'survey', ['id'], unique=False)

    if 'pnd_details' not in tables:
        op.create_table(
            'pnd_details',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('source_id', sa.Integer(), nullable=True),
            sa.Column('plan_id', sa.Integer(), nullable=True),
            sa.Column('plan_name', sa.String(), nullable=True),
            sa.Column('pillar_id', sa.Integer(), nullable=True),
            sa.Column('objective_id', sa.Integer(), nullable=True),
            sa.Column('strategy_id', sa.Integer(), nullable=True),
            sa.Column('component_id', sa.Integer(), nullable=True),
            sa.Column('pillar_description', sa.Text(), nullable=True),
            sa.Column('objective_description', sa.Text(), nullable=True),
            sa.Column('strategy_description', sa.Text(), nullable=True),
            sa.Column('component_description', sa.Text(), nullable=True),
            sa.Column('row_state', sa.Integer(), nullable=True),
            sa.Column('unique_identifier', sa.String(), nullable=True),
            sa.Column('selected_to_project', sa.Boolean(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
    if 'ix_pnd_details_id' not in _index_names('pnd_details'):
        op.create_index('ix_pnd_details_id', 'pnd_details', ['id'], unique=False)

    if 'project_localizations' not in tables:
        op.create_table(
            'project_localizations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('region', sa.String(), nullable=True),
            sa.Column('department', sa.String(), nullable=True),
            sa.Column('municipality', sa.String(), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
            sa.PrimaryKeyConstraint('id'),
        )
    if 'ix_project_localizations_id' not in _index_names('project_localizations'):
        op.create_index('ix_project_localizations_id', 'project_localizations', ['id'], unique=False)

    if 'indicator_code' not in _column_names('projects'):
        op.add_column('projects', sa.Column('indicator_code', sa.String(), nullable=True))


def downgrade() -> None:
    """Return to the previously recorded Alembic schema."""
    op.drop_column('projects', 'indicator_code')
    op.drop_index('ix_project_localizations_id', table_name='project_localizations')
    op.drop_table('project_localizations')
    op.drop_index('ix_pnd_details_id', table_name='pnd_details')
    op.drop_table('pnd_details')
    op.drop_index('ix_survey_id', table_name='survey')
    op.drop_table('survey')
    op.drop_index('ix_chat_history_session_id', table_name='chat_history')
    op.drop_index('ix_chat_history_id', table_name='chat_history')
    op.drop_table('chat_history')