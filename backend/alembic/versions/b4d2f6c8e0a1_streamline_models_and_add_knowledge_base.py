"""streamline_models_and_add_knowledge_base

Revision ID: b4d2f6c8e0a1
Revises: a3c1e2f4b5d6
Create Date: 2026-09-25 03:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4d2f6c8e0a1'
down_revision: Union[str, Sequence[str], None] = 'a3c1e2f4b5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add streamlined operational fields to disasters table
    op.add_column('disasters', sa.Column('title', sa.String(length=255), nullable=True))
    op.add_column('disasters', sa.Column('raw_telemetry', sa.JSON(), nullable=True))
    op.add_column('disasters', sa.Column('sitrep_summary', sa.Text(), nullable=True))
    op.add_column('disasters', sa.Column('recommended_actions', sa.JSON(), nullable=True))
    op.add_column('disasters', sa.Column('source_origin', sa.String(length=50), server_default='MANUAL', nullable=True))
    op.add_column('disasters', sa.Column('acknowledged', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    
    op.create_index(op.f('ix_disasters_title'), 'disasters', ['title'], unique=False)
    op.create_index(op.f('ix_disasters_acknowledged'), 'disasters', ['acknowledged'], unique=False)

    # 2. Make legacy ML columns nullable for backwards-compatible schema evolution
    op.alter_column('disasters', 'severity_score', existing_type=sa.Float(), nullable=True)
    op.alter_column('disasters', 'population_at_risk', existing_type=sa.Integer(), nullable=True)
    op.alter_column('disasters', 'confidence', existing_type=sa.Float(), nullable=True)

    # 3. Create knowledge_base table for RAG intelligence
    op.create_table(
        'knowledge_base',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_base_id'), 'knowledge_base', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_base_title'), 'knowledge_base', ['title'], unique=False)
    op.create_index(op.f('ix_knowledge_base_category'), 'knowledge_base', ['category'], unique=False)
    op.create_index(op.f('ix_knowledge_base_created_at'), 'knowledge_base', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop knowledge_base table
    op.drop_index(op.f('ix_knowledge_base_created_at'), table_name='knowledge_base')
    op.drop_index(op.f('ix_knowledge_base_category'), table_name='knowledge_base')
    op.drop_index(op.f('ix_knowledge_base_title'), table_name='knowledge_base')
    op.drop_index(op.f('ix_knowledge_base_id'), table_name='knowledge_base')
    op.drop_table('knowledge_base')

    # Drop disasters added columns
    op.drop_index(op.f('ix_disasters_acknowledged'), table_name='disasters')
    op.drop_index(op.f('ix_disasters_title'), table_name='disasters')
    op.drop_column('disasters', 'acknowledged')
    op.drop_column('disasters', 'source_origin')
    op.drop_column('disasters', 'recommended_actions')
    op.drop_column('disasters', 'sitrep_summary')
    op.drop_column('disasters', 'raw_telemetry')
    op.drop_column('disasters', 'title')
