"""add table likes and foreignkeys for tweets and users

Revision ID: bf8194eb5fbe
Revises: a35905adef8c
Create Date: 2024-09-17 15:31:33.417537

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bf8194eb5fbe"
down_revision: Union[str, None] = "a35905adef8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
