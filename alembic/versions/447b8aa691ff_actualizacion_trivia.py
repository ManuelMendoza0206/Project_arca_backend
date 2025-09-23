"""Actualizacion trivia

Revision ID: 447b8aa691ff
Revises: 901005cc538e
Create Date: 2025-09-22 23:32:25.585100

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '447b8aa691ff'
down_revision: Union[str, Sequence[str], None] = '901005cc538e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
