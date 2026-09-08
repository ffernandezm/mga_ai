"""preserve evaluation evidence when deleting a project

Revision ID: 5a8b2c3d4e11
Revises: 3f7a1c2d9e10
Create Date: 2026-09-08 20:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5a8b2c3d4e11"
down_revision: Union[str, Sequence[str], None] = "3f7a1c2d9e10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("evaluation_sessions") as batch_op:
        batch_op.alter_column("project_id", existing_type=sa.Integer(), nullable=True)
        batch_op.drop_constraint("evaluation_sessions_project_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "evaluation_sessions_project_id_fkey",
            "projects",
            ["project_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("evaluation_sessions") as batch_op:
        batch_op.drop_constraint("evaluation_sessions_project_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "evaluation_sessions_project_id_fkey",
            "projects",
            ["project_id"],
            ["id"],
        )
        batch_op.alter_column("project_id", existing_type=sa.Integer(), nullable=False)