"""create price_coefficient table

Revision ID: cac818787c31
Revises: 8e4bd2a7415d
Create Date: 2026-02-13 13:49:36.111528

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cac818787c31"
down_revision: Union[str, Sequence[str], None] = "8e4bd2a7415d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_coefficients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "complexity",
                "region",
                "discount",
                "seasonal",
                "promo",
                name="coefficienttype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("value", sa.Numeric(precision=8, scale=3), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_price_coefficients")),
    )


def downgrade() -> None:
    op.drop_table("price_coefficients")
