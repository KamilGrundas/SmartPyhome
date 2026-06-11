"""Rename email to username in user table

Revision ID: b3c4d5e6f7a8
Revises: fe56fa70289e
Create Date: 2026-06-11 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7a8'
down_revision = 'fe56fa70289e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('user', 'email', new_column_name='username')


def downgrade():
    op.alter_column('user', 'username', new_column_name='email')
