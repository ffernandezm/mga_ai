"""rename population fields and set defaults

Revision ID: a7f3c2b8e911
Revises: e2c11017a287
Create Date: 2026-05-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7f3c2b8e911'
down_revision: Union[str, Sequence[str], None] = 'e2c11017a287'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar columnas existentes en population
    op.alter_column('population', 'number_affected', new_column_name='population_number_affected')
    op.alter_column('population', 'source_information_affected', new_column_name='population_info_affected')
    op.alter_column('population', 'number_intervention', new_column_name='population_number_intervention')
    op.alter_column('population', 'source_information_intervention', new_column_name='population_info_intervention')

    # Asegurar valores por defecto "Personas" para los tipos
    op.execute("UPDATE population SET population_type_affected = 'Personas' WHERE population_type_affected IS NULL OR population_type_affected = ''")
    op.execute("UPDATE population SET population_type_intervention = 'Personas' WHERE population_type_intervention IS NULL OR population_type_intervention = '' OR population_type_intervention = 'No especificado'")

    # Hacer population_type_affected NOT NULL con default
    op.alter_column(
        'population',
        'population_type_affected',
        existing_type=sa.Text(),
        nullable=False,
        server_default='Personas',
    )
    op.alter_column(
        'population',
        'population_type_intervention',
        existing_type=sa.Text(),
        nullable=False,
        server_default='Personas',
    )

    # population_number_intervention pasa a ser nullable
    op.alter_column(
        'population',
        'population_number_intervention',
        existing_type=sa.Integer(),
        nullable=True,
        server_default=None,
    )


def downgrade() -> None:
    op.alter_column(
        'population',
        'population_number_intervention',
        existing_type=sa.Integer(),
        nullable=False,
        server_default='0',
    )
    op.alter_column(
        'population',
        'population_type_intervention',
        existing_type=sa.Text(),
        nullable=False,
        server_default='No especificado',
    )
    op.alter_column(
        'population',
        'population_type_affected',
        existing_type=sa.Text(),
        nullable=True,
        server_default=None,
    )

    op.alter_column('population', 'population_info_intervention', new_column_name='source_information_intervention')
    op.alter_column('population', 'population_number_intervention', new_column_name='number_intervention')
    op.alter_column('population', 'population_info_affected', new_column_name='source_information_affected')
    op.alter_column('population', 'population_number_affected', new_column_name='number_affected')
