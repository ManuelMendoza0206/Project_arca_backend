"""Actualizacion animals

Revision ID: 7d2563072184
Revises: be3f03f7e629
Create Date: 2025-09-22 23:28:40.992492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d2563072184'
down_revision: Union[str, Sequence[str], None] = 'be3f03f7e629'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
