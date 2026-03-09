"""Update courses table: rename credits→units, add level; add program_courses junction;
drop orphaned singular tables created by migration 001.

Revision ID: 003_update_courses_table
Revises: 002_programs_table
Create Date: 2026-03-08

"""
from alembic import op
import sqlalchemy as sa

revision = '003_update_courses_table'
down_revision = '002_programs_table'
branch_labels = None
depends_on = None


def upgrade():
    # ── 1. Drop orphaned empty singular tables from migration 001 ──────────
    # student_course must go first because it holds FKs to course and student
    op.drop_table('student_course')
    op.drop_table('course')
    op.drop_table('student')

    # ── 2. Rename credits → units on courses ──────────────────────────────
    op.alter_column('courses', 'credits', new_column_name='units')

    # ── 3. Add level column to courses ────────────────────────────────────
    # Values from the catalog: "Graduate", "Graduate Core", "Advanced Graduate",
    # "Graduate (300-level)", "Graduate Lab"
    op.add_column('courses', sa.Column('level', sa.String(50), nullable=True))

    # ── 4. Create program_courses junction table ───────────────────────────
    # A course (e.g. Robotics I) can appear under multiple programs.
    op.create_table(
        'program_courses',
        sa.Column('program_id', sa.String(50), nullable=False),
        sa.Column('course_id', sa.String(20), nullable=False),
        sa.ForeignKeyConstraint(['program_id'], ['programs.program_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('program_id', 'course_id'),
    )
    op.create_index('ix_program_courses_program_id', 'program_courses', ['program_id'])
    op.create_index('ix_program_courses_course_id', 'program_courses', ['course_id'])


def downgrade():
    op.drop_index('ix_program_courses_course_id', table_name='program_courses')
    op.drop_index('ix_program_courses_program_id', table_name='program_courses')
    op.drop_table('program_courses')

    op.drop_column('courses', 'level')
    op.alter_column('courses', 'units', new_column_name='credits')

    # Recreate singular orphan tables so migration 002 can cleanly downgrade
    op.create_table(
        'course',
        sa.Column('id', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=True),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'student',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(120), nullable=False),
        sa.Column('password_hash', sa.String(256), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('major', sa.String(100), nullable=True),
        sa.Column('year', sa.String(20), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
        sa.Column('career_goals', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_table(
        'student_course',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['course.id']),
        sa.ForeignKeyConstraint(['student_id'], ['student.id']),
        sa.PrimaryKeyConstraint('id'),
    )
