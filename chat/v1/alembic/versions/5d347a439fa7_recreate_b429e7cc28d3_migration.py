"""Recreate b429e7cc28d3 migration

Revision ID: 5d347a439fa7
Revises: 
Create Date: 2024-11-06 21:42:58.011836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d347a439fa7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
