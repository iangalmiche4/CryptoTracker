"""add user_holdings table

Revision ID: 70e9d372b804
Revises: a76d8e961773
Create Date: 2026-04-01 10:40:35.644268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70e9d372b804'
down_revision: Union[str, None] = 'a76d8e961773'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_holdings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('coin_id', sa.String(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('purchase_price', sa.Float(), nullable=False),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_holdings_user_id', 'user_holdings', ['user_id'])
    op.create_index('ix_user_holdings_coin_id', 'user_holdings', ['coin_id'])


def downgrade() -> None:
    op.drop_index('ix_user_holdings_coin_id', table_name='user_holdings')
    op.drop_index('ix_user_holdings_user_id', table_name='user_holdings')
    op.drop_table('user_holdings')
