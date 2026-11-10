"""Criação da tabela `recommendation_runs` para auditoria e persistência de recomendações (RN-10).

Revision ID: 0002_recommendations
Revises: 0001_initial_schema
Create Date: 2026-11-10 00:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_recommendations"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recommendation_runs",
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("generated_at", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("prompt_version", sa.String(length=32), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("warnings_json", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["upload_id"],
            ["uploads.upload_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_index(
        op.f("ix_recommendation_runs_run_id"),
        "recommendation_runs",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_runs_upload_id"),
        "recommendation_runs",
        ["upload_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recommendation_runs_generated_at"),
        "recommendation_runs",
        ["generated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_recommendation_runs_generated_at"),
        table_name="recommendation_runs",
    )
    op.drop_index(
        op.f("ix_recommendation_runs_upload_id"),
        table_name="recommendation_runs",
    )
    op.drop_index(
        op.f("ix_recommendation_runs_run_id"),
        table_name="recommendation_runs",
    )
    op.drop_table("recommendation_runs")
