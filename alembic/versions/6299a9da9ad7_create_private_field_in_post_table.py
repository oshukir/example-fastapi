"""create private field in Post table

Revision ID: 6299a9da9ad7
Revises: d6dc2b5c6a73
Create Date: 2026-03-24 16:50:54.049391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6299a9da9ad7'
down_revision: Union[str, Sequence[str], None] = 'd6dc2b5c6a73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('is_private', sa.Boolean(), server_default='FALSE', nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'is_private')
    pass
