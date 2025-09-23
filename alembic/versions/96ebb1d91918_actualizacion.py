"""Actualizacion 

Revision ID: 96ebb1d91918
Revises: 6fd3b1e8a1f7
Create Date: 2025-09-23 12:11:56.334428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96ebb1d91918'
down_revision: Union[str, Sequence[str], None] = '6fd3b1e8a1f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
