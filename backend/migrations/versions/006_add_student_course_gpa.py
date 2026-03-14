"""Add per-course GPA field on student_courses.

Revision ID: 006_add_student_course_gpa
Revises: 005_add_grade_and_gpa_fields
Create Date: 2026-03-13
"""
from alembic import op
import sqlalchemy as sa

revision = '006_add_student_course_gpa'
down_revision = '005_add_grade_and_gpa_fields'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('student_courses') as batch_op:
        batch_op.add_column(sa.Column('course_gpa', sa.Float(), nullable=True))

    # Backfill existing graded rows for compatibility.
    op.execute("UPDATE student_courses SET course_gpa = grade_points WHERE course_gpa IS NULL AND grade_points IS NOT NULL")


def downgrade():
    with op.batch_alter_table('student_courses') as batch_op:
        batch_op.drop_column('course_gpa')
