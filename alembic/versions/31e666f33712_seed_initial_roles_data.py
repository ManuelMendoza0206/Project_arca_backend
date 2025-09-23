"""Seed initial roles data

Revision ID: 31e666633712
Revises: 68ec98c1dab9
Create Date: 2025-09-19 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '31e666633712'  
down_revision = '68ec98c1da8b'
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.execute("""
        INSERT INTO roles (id, name) VALUES
        (1, 'administrador'),
        (4, 'veterinario'),
        (3, 'cuidador'),
        (2, 'visitante')
        ON CONFLICT (id) DO NOTHING;
    """)



def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id IN (1, 2, 3, 4);")
