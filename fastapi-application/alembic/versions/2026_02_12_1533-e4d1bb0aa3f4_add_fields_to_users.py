"""add fields to users

Revision ID: e4d1bb0aa3f4
Revises: a64a5c0c7658
Create Date: 2026-02-12 15:33:40.295597

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e4d1bb0aa3f4"
down_revision: Union[str, Sequence[str], None] = "a64a5c0c7658"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("telegram_id", sa.BigInteger(), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("is_blocked", sa.Boolean(), nullable=False))
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_unique_constraint(op.f("uq_users_telegram_id"), "users", ["telegram_id"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_users_telegram_id"), "users", type_="unique")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "is_blocked")
    op.drop_column("users", "name")
    op.drop_column("users", "phone")
    op.drop_column("users", "telegram_id")
