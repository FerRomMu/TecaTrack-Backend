"""add cbu as string and add constraint

Revision ID: 84d06d592174
Revises: 4d4dcad48d6b
Create Date: 2026-04-18 13:35:45.507443

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "84d06d592174"
down_revision: str | Sequence[str] | None = "4d4dcad48d6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("accounts", sa.Column("cbu", sa.CHAR(length=22), nullable=False))
    op.create_check_constraint("ck_cbu_format", "accounts", "cbu ~ '^[0-9]{22}$'")
    op.create_unique_constraint("uq_accounts_cbu", "accounts", ["cbu"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_accounts_cbu", "accounts", type_="unique")
    op.drop_constraint("ck_cbu_format", "accounts", type_="check")
    op.drop_column("accounts", "cbu")
