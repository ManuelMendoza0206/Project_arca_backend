"""Actualizacion animals2.0

Revision ID: f1dcbe6a1b2a
Revises: 447b8aa691ff
Create Date: 2025-09-23 00:09:09.019880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1dcbe6a1b2a'
down_revision: Union[str, Sequence[str], None] = '447b8aa691ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
