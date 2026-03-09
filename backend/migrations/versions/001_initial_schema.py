"""Initial schema: courses, students, student_courses

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-08 13:37:22.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'course',
        sa.Column('id', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('prerequisites', postgresql.JSON(astext_type=sa.Text()), nullable=True),
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
        sa.Column('interests', postgresql.JSON(astext_type=sa.Text()), nullable=True),
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


def downgrade():
    op.drop_table('student_course')
    op.drop_table('student')
    op.drop_table('course')
