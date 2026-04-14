from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6301427ba51c"
down_revision: str | Sequence[str] | None = "589003c7401f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    receipt_status_enum = sa.Enum(
        "PENDING", "PROCESSED", "FAILED", name="receipt_status"
    )
    receipt_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_index(op.f("ix_accounts_user_id"), "accounts", ["user_id"], unique=False)

    op.alter_column(
        "receipts",
        "status",
        existing_type=sa.TEXT(),
        type_=receipt_status_enum,
        existing_nullable=False,
        postgresql_using="status::receipt_status",
    )

    op.create_index(op.f("ix_receipts_file_id"), "receipts", ["file_id"], unique=False)
    op.create_index(op.f("ix_receipts_user_id"), "receipts", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_transactions_from_account_id"),
        "transactions",
        ["from_account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transactions_receipt_id"), "transactions", ["receipt_id"], unique=False
    )
    op.create_index(
        op.f("ix_transactions_receiver_user_id"),
        "transactions",
        ["receiver_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transactions_sender_user_id"),
        "transactions",
        ["sender_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transactions_to_account_id"),
        "transactions",
        ["to_account_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_transactions_to_account_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_sender_user_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_receiver_user_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_receipt_id"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_from_account_id"), table_name="transactions")
    op.drop_index(op.f("ix_receipts_user_id"), table_name="receipts")
    op.drop_index(op.f("ix_receipts_file_id"), table_name="receipts")

    op.alter_column(
        "receipts",
        "status",
        existing_type=sa.Enum("PENDING", "PROCESSED", "FAILED", name="receipt_status"),
        type_=sa.TEXT(),
        existing_nullable=False,
    )

    op.drop_index(op.f("ix_accounts_user_id"), table_name="accounts")

    receipt_status_enum = sa.Enum(
        "PENDING", "PROCESSED", "FAILED", name="receipt_status"
    )
    receipt_status_enum.drop(op.get_bind(), checkfirst=True)
