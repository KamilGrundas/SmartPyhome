"""Add access log table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'accesslog',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('uid', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('gate_name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_accesslog_timestamp', 'accesslog', ['timestamp'])


def downgrade():
    op.drop_index('ix_accesslog_timestamp', 'accesslog')
    op.drop_table('accesslog')
