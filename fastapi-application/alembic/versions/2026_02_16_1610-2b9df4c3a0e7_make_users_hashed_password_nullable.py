"""make users hashed_password nullable

Revision ID: 2b9df4c3a0e7
Revises: 5c3a9e9b7a1f
Create Date: 2026-02-16 16:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2b9df4c3a0e7"
down_revision: Union[str, Sequence[str], None] = "5c3a9e9b7a1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=1024),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=1024),
        nullable=False,
    )
