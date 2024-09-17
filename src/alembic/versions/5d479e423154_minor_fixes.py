"""minor fixes

Revision ID: 5d479e423154
Revises: bf8194eb5fbe
Create Date: 2024-09-17 15:46:03.819813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d479e423154'
down_revision: Union[str, None] = 'bf8194eb5fbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
