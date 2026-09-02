"""ajustar tabla de plan de desarrollo

Revision ID: 4e009d45e038
Revises: c3bcc6e2df7c
Create Date: 2026-03-16 23:24:07.853316

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '4e009d45e038'
down_revision: Union[str, Sequence[str], None] = 'c3bcc6e2df7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
