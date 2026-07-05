"""add completed order status

Revision ID: 6a7b8c9d0e1f
Revises: 2f66f643b6e4
Create Date: 2026-07-05 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '6a7b8c9d0e1f'
down_revision: Union[str, None] = '2f66f643b6e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE 'COMPLETED'")


def downgrade() -> None:
    op.execute("ALTER TYPE orderstatus RENAME TO orderstatus_old")
    op.execute("CREATE TYPE orderstatus AS ENUM('PENDING', 'CONFIRMED', 'CANCELLED')")
    op.execute("ALTER TABLE orders ALTER COLUMN status TYPE orderstatus USING status::text::orderstatus")
    op.execute("DROP TYPE orderstatus_old")
