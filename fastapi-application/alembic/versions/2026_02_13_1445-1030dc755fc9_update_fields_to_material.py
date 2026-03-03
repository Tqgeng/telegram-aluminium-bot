"""update fields to  material

Revision ID: 1030dc755fc9
Revises: 9feca534536e
Create Date: 2026-02-13 14:45:15.776868

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1030dc755fc9"
down_revision: Union[str, Sequence[str], None] = "9feca534536e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "materials",
        sa.Column("price_per_unit", sa.Numeric(precision=12, scale=2), nullable=False),
    )
    op.drop_column("materials", "price_per_init")


def downgrade() -> None:
    op.add_column(
        "materials",
        sa.Column(
            "price_per_init",
            sa.NUMERIC(precision=12, scale=2),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("materials", "price_per_unit")
