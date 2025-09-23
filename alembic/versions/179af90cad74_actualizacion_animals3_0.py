"""Actualizacion animals3.0

Revision ID: 179af90cad74
Revises: f1dcbe6a1b2a
Create Date: 2025-09-23 09:05:34.593870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '179af90cad74'
down_revision: Union[str, Sequence[str], None] = 'f1dcbe6a1b2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
