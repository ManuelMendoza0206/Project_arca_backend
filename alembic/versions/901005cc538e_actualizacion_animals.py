"""Actualizacion animals

Revision ID: 901005cc538e
Revises: 7d2563072184
Create Date: 2025-09-22 23:31:08.597929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '901005cc538e'
down_revision: Union[str, Sequence[str], None] = '7d2563072184'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
