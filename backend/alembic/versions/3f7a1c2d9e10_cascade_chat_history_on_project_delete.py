"""cascade operational chat history when deleting a project

Revision ID: 3f7a1c2d9e10
Revises: c4a9d7e91b23
Create Date: 2026-09-08 20:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "3f7a1c2d9e10"
down_revision: Union[str, Sequence[str], None] = "c4a9d7e91b23"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("chat_history") as batch_op:
        batch_op.drop_constraint("chat_history_project_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "chat_history_project_id_fkey",
            "projects",
            ["project_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("chat_history") as batch_op:
        batch_op.drop_constraint("chat_history_project_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "chat_history_project_id_fkey",
            "projects",
            ["project_id"],
            ["id"],
        )