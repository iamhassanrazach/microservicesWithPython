"""create activities table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'activities',
        sa.Column('id',               sa.String(), nullable=False),
        sa.Column('user_id',          sa.String(), nullable=False),
        sa.Column('game_id',          sa.String(), nullable=False),
        sa.Column('action',           sa.String(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('created_at',       sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_activities_user_id', 'activities', ['user_id'])


def downgrade():
    op.drop_index('ix_activities_user_id', table_name='activities')
    op.drop_table('activities')
