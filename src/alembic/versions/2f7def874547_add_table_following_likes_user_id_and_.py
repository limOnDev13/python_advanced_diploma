"""add table following; likes.user_id and likes.tweet_id now is not nullable

Revision ID: 2f7def874547
Revises: 5d479e423154
Create Date: 2024-09-18 10:31:27.825798

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f7def874547"
down_revision: Union[str, None] = "5d479e423154"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "following",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("follower_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["follower_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("author_id", "follower_id", name="unq_following"),
    )
    op.alter_column("likes", "user_id", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column("likes", "tweet_id", existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("likes", "tweet_id", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column("likes", "user_id", existing_type=sa.INTEGER(), nullable=True)
    op.drop_table("following")
    # ### end Alembic commands ###
