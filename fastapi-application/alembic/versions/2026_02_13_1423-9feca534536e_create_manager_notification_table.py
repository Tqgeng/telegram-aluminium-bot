"""create manager_notification table

Revision ID: 9feca534536e
Revises: 6294a536105e
Create Date: 2026-02-13 14:23:29.405640

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9feca534536e"
down_revision: Union[str, Sequence[str], None] = "6294a536105e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "manager_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.BigInteger(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column(
            "notified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            name=op.f("fk_manager_notifications_application_id_applications"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_manager_notifications")),
    )


def downgrade() -> None:
    op.drop_table("manager_notifications")
