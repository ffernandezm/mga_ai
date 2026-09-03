"""Add evaluation telemetry tables.

Revision ID: 9d4e8b2c1f07
Revises: a7f3c2b8e911
"""

from alembic import op
import sqlalchemy as sa


revision = "9d4e8b2c1f07"
down_revision = "a7f3c2b8e911"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "evaluation_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("participant_id", sa.String(length=128), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("task", sa.String(length=160), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=True),
        sa.Column("configuration", sa.JSON(), nullable=False),
    )
    op.create_index("ix_evaluation_sessions_participant_id", "evaluation_sessions", ["participant_id"])
    op.create_index("ix_evaluation_sessions_project_id", "evaluation_sessions", ["project_id"])
    op.create_table(
        "evaluation_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("evaluation_session_id", sa.Integer(), sa.ForeignKey("evaluation_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("section", sa.String(length=80), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("task", sa.String(length=160), nullable=True),
        sa.Column("llm_duration_ms", sa.Integer(), nullable=True),
        sa.Column("rag_enabled", sa.Boolean(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_evaluation_events_evaluation_session_id", "evaluation_events", ["evaluation_session_id"])


def downgrade():
    op.drop_index("ix_evaluation_events_evaluation_session_id", table_name="evaluation_events")
    op.drop_table("evaluation_events")
    op.drop_index("ix_evaluation_sessions_project_id", table_name="evaluation_sessions")
    op.drop_index("ix_evaluation_sessions_participant_id", table_name="evaluation_sessions")
    op.drop_table("evaluation_sessions")