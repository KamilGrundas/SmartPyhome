"""Add RFID access tables

Revision ID: a1b2c3d4e5f6
Revises: 1a31ce608336
Create Date: 2026-06-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision = 'a1b2c3d4e5f6'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'accesspoint',
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'accessgroup',
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'accesscard',
        sa.Column('uid', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uid'),
    )

    op.create_table(
        'cardgroup',
        sa.Column('card_id', sa.Uuid(), nullable=False),
        sa.Column('group_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['accesscard.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['accessgroup.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('card_id', 'group_id'),
    )

    op.create_table(
        'cardaccesspoint',
        sa.Column('card_id', sa.Uuid(), nullable=False),
        sa.Column('point_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['card_id'], ['accesscard.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['point_id'], ['accesspoint.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('card_id', 'point_id'),
    )

    op.create_table(
        'groupaccesspoint',
        sa.Column('group_id', sa.Uuid(), nullable=False),
        sa.Column('point_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['accessgroup.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['point_id'], ['accesspoint.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('group_id', 'point_id'),
    )


def downgrade():
    op.drop_table('groupaccesspoint')
    op.drop_table('cardaccesspoint')
    op.drop_table('cardgroup')
    op.drop_table('accesscard')
    op.drop_table('accessgroup')
    op.drop_table('accesspoint')
