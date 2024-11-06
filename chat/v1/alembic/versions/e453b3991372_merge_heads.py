"""merge heads

Revision ID: e453b3991372
Revises: 5d347a439fa7, b429e7cc28d3
Create Date: 2024-11-06 22:52:33.357499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e453b3991372'
down_revision: Union[str, None] = ('5d347a439fa7', 'b429e7cc28d3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
