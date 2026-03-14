"""Add course grade fields and student program GPA.

Revision ID: 005_add_grade_and_gpa_fields
Revises: 004_student_uni_program
Create Date: 2026-03-13
"""
from alembic import op
import sqlalchemy as sa

revision = '005_add_grade_and_gpa_fields'
down_revision = '004_student_uni_program'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('student_courses') as batch_op:
        batch_op.add_column(sa.Column('final_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('final_letter', sa.String(length=5), nullable=True))
        batch_op.add_column(sa.Column('grade_points', sa.Float(), nullable=True))

    with op.batch_alter_table('students') as batch_op:
        batch_op.add_column(sa.Column('program_gpa', sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table('students') as batch_op:
        batch_op.drop_column('program_gpa')

    with op.batch_alter_table('student_courses') as batch_op:
        batch_op.drop_column('grade_points')
        batch_op.drop_column('final_letter')
        batch_op.drop_column('final_score')
