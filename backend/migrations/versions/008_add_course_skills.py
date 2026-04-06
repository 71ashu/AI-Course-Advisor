"""Add skills JSON column to courses.

Revision ID: 008_add_course_skills
Revises: 007_student_profile_extensions
Create Date: 2026-04-05
"""
from alembic import op
import sqlalchemy as sa

revision = '008_add_course_skills'
down_revision = '007_student_profile_extensions'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('courses', sa.Column('skills', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('courses', 'skills')
