"""add comments table

Revision ID: d6dc2b5c6a73
Revises: 4d10615f6adf
Create Date: 2026-03-16 00:48:31.752087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6dc2b5c6a73'
down_revision: Union[str, Sequence[str], None] = '4d10615f6adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False)
    )

    op.create_foreign_key(
        'comments_users_fk',
        source_table="comments",
        referent_table="users",
        local_cols=['owner_id'],
        remote_cols=['id'],
        ondelete="CASCADE"
    )

    op.create_foreign_key(
        'comments_posts_fk',
        source_table="comments",
        referent_table="posts",
        local_cols=['post_id'],
        remote_cols=['id'],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('comments')
