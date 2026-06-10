"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2026-06-10 08:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Create logs table
    op.create_table(
        'logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logs_id'), 'logs', ['id'], unique=False)
    op.create_index(op.f('ix_logs_level'), 'logs', ['level'], unique=False)
    op.create_index(op.f('ix_logs_service'), 'logs', ['service'], unique=False)
    op.create_index(op.f('ix_logs_timestamp'), 'logs', ['timestamp'], unique=False)

    # 3. Create alert_rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('threshold', sa.Integer(), nullable=False),
        sa.Column('window_minutes', sa.Integer(), nullable=False),
        sa.Column('notify_email', sa.String(length=255), nullable=False),
        sa.Column('notify_webhook_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_rules_id'), 'alert_rules', ['id'], unique=False)
    op.create_index(op.f('ix_alert_rules_service'), 'alert_rules', ['service'], unique=False)

    # 4. Create alert_history table
    op.create_table(
        'alert_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.Column('threshold', sa.Integer(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notified_email', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_history_id'), 'alert_history', ['id'], unique=False)
    op.create_index(op.f('ix_alert_history_service'), 'alert_history', ['service'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alert_history_service'), table_name='alert_history')
    op.drop_index(op.f('ix_alert_history_id'), table_name='alert_history')
    op.drop_table('alert_history')
    op.drop_index(op.f('ix_alert_rules_service'), table_name='alert_rules')
    op.drop_index(op.f('ix_alert_rules_id'), table_name='alert_rules')
    op.drop_table('alert_rules')
    op.drop_index(op.f('ix_logs_timestamp'), table_name='logs')
    op.drop_index(op.f('ix_logs_service'), table_name='logs')
    op.drop_index(op.f('ix_logs_level'), table_name='logs')
    op.drop_index(op.f('ix_logs_id'), table_name='logs')
    op.drop_table('logs')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
