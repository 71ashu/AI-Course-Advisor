"""Add university and program fields to students.

Revision ID: 004_student_uni_program
Revises: 003_update_courses_table
Create Date: 2026-03-11
"""
from alembic import op
import sqlalchemy as sa

revision = '004_student_uni_program'
down_revision = '003_update_courses_table'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('students') as batch_op:
        batch_op.add_column(sa.Column('university', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('program_enrolled', sa.String(length=200), nullable=True))


def downgrade():
    with op.batch_alter_table('students') as batch_op:
        batch_op.drop_column('program_enrolled')
        batch_op.drop_column('university')
