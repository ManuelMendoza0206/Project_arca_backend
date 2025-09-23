"""Actualizacion animals

Revision ID: be3f03f7e629
Revises: 06bbdf3830f2
Create Date: 2025-09-22 23:28:01.287643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be3f03f7e629'
down_revision: Union[str, Sequence[str], None] = '06bbdf3830f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
