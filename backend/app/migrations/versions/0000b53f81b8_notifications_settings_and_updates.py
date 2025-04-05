"""notifications,settings and updates

Revision ID: 0000b53f81b8
Revises: 8ad9bcdec959
Create Date: 2025-04-05 12:19:50.860974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0000b53f81b8'
down_revision: Union[str, None] = '8ad9bcdec959'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
