"""add_cuil_to_users

Revision ID: 81f3e396c8cf
Revises: 84d06d592174
Create Date: 2026-04-19 19:37:41.529815

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "81f3e396c8cf"
down_revision: str | Sequence[str] | None = "84d06d592174"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("cuil", sa.CHAR(length=11), nullable=True))

    # backfill con algo único (asumiendo que existe users.id)
    op.execute("""
        UPDATE users
        SET cuil = LPAD(id::text, 11, '0')
        WHERE cuil IS NULL
    """)

    op.alter_column("users", "cuil", nullable=False)

    op.create_unique_constraint("uq_users_cuil", "users", ["cuil"])
    op.create_check_constraint(
        "ck_cuil_format",
        "users",
        "cuil ~ '^[0-9]{11}$'",
    )


def downgrade() -> None:
    op.drop_constraint("ck_cuil_format", "users", type_="check")
    op.drop_constraint("uq_users_cuil", "users", type_="unique")
    op.drop_column("users", "cuil")
