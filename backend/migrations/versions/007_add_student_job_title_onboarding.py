"""Add target job title, synthetic flag, and onboarding flag to students.

Revision ID: 007_student_profile_extensions
Revises: 006_add_student_course_gpa
Create Date: 2026-04-04
"""
from alembic import op
import sqlalchemy as sa

revision = '007_student_profile_extensions'
down_revision = '006_add_student_course_gpa'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('students') as batch_op:
        batch_op.add_column(sa.Column('target_job_title', sa.String(length=200), nullable=True))
        batch_op.add_column(
            sa.Column('is_synthetic', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        )
        batch_op.add_column(
            sa.Column(
                'onboarding_completed',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false'),
            ),
        )


def downgrade():
    with op.batch_alter_table('students') as batch_op:
        batch_op.drop_column('onboarding_completed')
        batch_op.drop_column('is_synthetic')
        batch_op.drop_column('target_job_title')
