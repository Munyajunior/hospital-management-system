"""add_profile_picture_type_column

Revision ID: 8ad9bcdec959
Revises: 3b5be424b925
Create Date: 2025-04-02 19:23:10.728400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ad9bcdec959'
down_revision: Union[str, None] = '3b5be424b925'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('profile_picture_type', sa.String(50), nullable=True))
    op.add_column('patients', sa.Column('profile_picture_type', sa.String(50), nullable=True))

def downgrade():
    op.drop_column('users', 'profile_picture_type')
    op.drop_column('patients', 'profile_picture_type')
