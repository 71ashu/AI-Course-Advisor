"""Add programs table for SCU graduate program catalog

Revision ID: 002_programs_table
Revises: 001_initial_schema
Create Date: 2026-03-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_programs_table'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'programs',
        sa.Column('program_id', sa.String(50), nullable=False),
        sa.Column('program_name', sa.String(200), nullable=False),
        sa.Column('degree_type', sa.String(50), nullable=False),
        sa.Column('department', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_units_required', sa.Integer(), nullable=True),
        sa.Column('minimum_gpa', sa.Float(), nullable=True),

        # JSONB for rich querying on nested requirement structures
        sa.Column('requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('concentrations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_outcomes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('admission_requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Optional fields present only on select programs
        sa.Column('special_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('time_limit', sa.String(200), nullable=True),

        sa.PrimaryKeyConstraint('program_id'),
    )

    # GIN indexes to allow efficient queries inside the JSONB columns
    op.create_index(
        'ix_programs_requirements',
        'programs',
        [sa.text("requirements jsonb_path_ops")],
        postgresql_using='gin',
    )
    op.create_index(
        'ix_programs_admission_requirements',
        'programs',
        [sa.text("admission_requirements jsonb_path_ops")],
        postgresql_using='gin',
    )


def downgrade():
    op.drop_index('ix_programs_admission_requirements', table_name='programs')
    op.drop_index('ix_programs_requirements', table_name='programs')
    op.drop_table('programs')
