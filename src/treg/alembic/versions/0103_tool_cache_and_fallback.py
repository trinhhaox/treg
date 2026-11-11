"""Add cache_ttl_seconds and fallback_tool_id to Tool table, create tool_cache table.

Revision ID: 0103
Revises: 0102
Create Date: 2026-11-12
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0103"
down_revision: str | Sequence[str] | None = "0102"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("tool") as batch:
        batch.add_column(sa.Column("cache_ttl_seconds", sa.Integer(), nullable=True, server_default="0"))
        batch.add_column(sa.Column("fallback_tool_id", sa.Integer(), nullable=True))

    op.create_table(
        "tool_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tool.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("org.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("cache_key", sa.String(length=64), nullable=False, index=True),
        sa.Column("method", sa.String(length=16), nullable=False, server_default="GET"),
        sa.Column("path_url", sa.String(length=1024), nullable=False, server_default=""),
        sa.Column("status_code", sa.Integer(), nullable=False, server_default="200"),
        sa.Column("headers_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("response_body", sa.LargeBinary(), nullable=False),
        sa.Column("body_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False, index=True),
    )
    op.create_index("ix_tool_cache_key", "tool_cache", ["tool_id", "cache_key"], unique=True)


def downgrade() -> None:
    op.drop_table("tool_cache")
    with op.batch_alter_table("tool") as batch:
        batch.drop_column("fallback_tool_id")
        batch.drop_column("cache_ttl_seconds")

