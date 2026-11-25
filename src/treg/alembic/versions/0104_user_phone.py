"""Add phone column to User table for phone-based login and verification.

Revision ID: 0104
Revises: 0103
Create Date: 2026-11-25
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0104"
down_revision: str | Sequence[str] | None = "0103"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("user") as batch:
        batch.add_column(sa.Column("phone", sa.String(), nullable=True))
        batch.create_index("ix_user_phone", ["phone"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("user") as batch:
        batch.drop_index("ix_user_phone")
        batch.drop_column("phone")
