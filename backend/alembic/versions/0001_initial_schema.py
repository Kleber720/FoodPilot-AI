"""Criação das tabelas iniciais `uploads` e `order_items`.

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-11-09 18:40:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "uploads",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.String(length=64), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("valid_orders_count", sa.Integer(), nullable=False),
        sa.Column("canceled_orders_count", sa.Integer(), nullable=False),
        sa.Column("summary_metrics_json", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("upload_id"),
    )
    op.create_index(op.f("ix_uploads_created_at"), "uploads", ["created_at"], unique=False)
    op.create_index(op.f("ix_uploads_upload_id"), "uploads", ["upload_id"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.String(length=128), nullable=False),
        sa.Column("timestamp", sa.String(length=64), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("discount", sa.Float(), nullable=False),
        sa.Column("prep_time_minutes", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["upload_id"],
            ["uploads.upload_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_items_order_id"), "order_items", ["order_id"], unique=False)
    op.create_index(op.f("ix_order_items_upload_id"), "order_items", ["upload_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_order_items_upload_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_table("order_items")
    op.drop_index(op.f("ix_uploads_upload_id"), table_name="uploads")
    op.drop_index(op.f("ix_uploads_created_at"), table_name="uploads")
    op.drop_table("uploads")
