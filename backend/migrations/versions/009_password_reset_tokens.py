"""password reset tokens table

Revision ID: 009_password_reset_tokens
Revises: 4fb6f2ebf8c2
Create Date: 2026-05-17
"""
from alembic import op
import sqlalchemy as sa

revision = '009_password_reset_tokens'
down_revision = '4fb6f2ebf8c2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
    )
    op.create_index('ix_password_reset_tokens_student_id', 'password_reset_tokens', ['student_id'], unique=False)


def downgrade():
    op.drop_index('ix_password_reset_tokens_student_id', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
