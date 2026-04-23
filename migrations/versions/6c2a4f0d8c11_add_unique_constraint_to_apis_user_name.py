"""add unique constraint to apis user_name

Revision ID: 6c2a4f0d8c11
Revises: 47e17e98c268
Create Date: 2026-04-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6c2a4f0d8c11"
down_revision: Union[str, Sequence[str], None] = "47e17e98c268"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint("uq_apis_user_name", "apis", ["user_name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_apis_user_name", "apis", type_="unique")
