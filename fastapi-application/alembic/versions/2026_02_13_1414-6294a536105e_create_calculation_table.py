"""create calculation table

Revision ID: 6294a536105e
Revises: cac818787c31
Create Date: 2026-02-13 14:14:51.611766

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6294a536105e"
down_revision: Union[str, Sequence[str], None] = "cac818787c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "calculations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("construction_type", sa.String(length=64), nullable=False),
        sa.Column("profile_system", sa.String(length=128), nullable=True),
        sa.Column("width", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("height", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("area", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("material_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("labor_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "additional_cost",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column("total_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_calculations_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_calculations")),
    )


def downgrade() -> None:
    op.drop_table("calculations")
