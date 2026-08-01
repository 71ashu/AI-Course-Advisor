"""Add alt_codes JSON column to courses for cross-listed course numbers
(e.g. EMGT 330 is also listed as ENGR 330 / GREN 330).

Revision ID: 010_add_course_alt_codes
Revises: 009_password_reset_tokens
Create Date: 2026-08-01
"""
from alembic import op
import sqlalchemy as sa

revision = '010_add_course_alt_codes'
down_revision = '009_password_reset_tokens'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('courses', sa.Column('alt_codes', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('courses', 'alt_codes')
