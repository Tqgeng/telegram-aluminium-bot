"""make users email nullable

Revision ID: 5c3a9e9b7a1f
Revises: 1030dc755fc9
Create Date: 2026-02-16 16:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5c3a9e9b7a1f"
down_revision: Union[str, Sequence[str], None] = "1030dc755fc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=320),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=320),
        nullable=False,
    )
