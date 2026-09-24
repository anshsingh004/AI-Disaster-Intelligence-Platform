"""add_report_ai_content_columns

Revision ID: a3c1e2f4b5d6
Revises: f9b96611aa61
Create Date: 2026-07-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c1e2f4b5d6'
down_revision: Union[str, Sequence[str], None] = 'f9b96611aa61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AI-generated report content columns to the reports table."""
    op.add_column('reports', sa.Column('executive_summary', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('situation_analysis', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('disaster_classification', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('risk_assessment', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('population_impact', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('infrastructure_impact', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('ai_confidence_note', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('forecast', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('recommended_actions', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('data_sources', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove AI-generated report content columns from the reports table."""
    op.drop_column('reports', 'data_sources')
    op.drop_column('reports', 'recommended_actions')
    op.drop_column('reports', 'forecast')
    op.drop_column('reports', 'ai_confidence_note')
    op.drop_column('reports', 'infrastructure_impact')
    op.drop_column('reports', 'population_impact')
    op.drop_column('reports', 'risk_assessment')
    op.drop_column('reports', 'disaster_classification')
    op.drop_column('reports', 'situation_analysis')
    op.drop_column('reports', 'executive_summary')
