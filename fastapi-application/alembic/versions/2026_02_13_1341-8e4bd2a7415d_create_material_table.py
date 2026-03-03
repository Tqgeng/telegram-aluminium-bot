"""create material table

Revision ID: 8e4bd2a7415d
Revises: 0c02c8371646
Create Date: 2026-02-13 13:41:32.378090

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8e4bd2a7415d"
down_revision: Union[str, Sequence[str], None] = "0c02c8371646"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "windows",
                "doors",
                "facades",
                "partitions",
                "showcases",
                "others",
                name="materialcategory",
            ),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Enum(
                "profile",
                "glazing",
                "fittings",
                "components",
                name="materialtype",
            ),
            nullable=False,
        ),
        sa.Column("price_per_init", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("in_stock", sa.Boolean(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_materials")),
    )


def downgrade() -> None:
    op.drop_table("materials")
