"""add Follows table

Revision ID: bc531810d645
Revises: 232da975ab30
Create Date: 2023-12-20 02:34:57.207741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc531810d645"
down_revision: Union[str, None] = "232da975ab30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "follows",
        sa.Column("follower_id", sa.Uuid(), nullable=False),
        sa.Column("artist_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
        ),
        sa.ForeignKeyConstraint(
            ["follower_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("follower_id", "artist_id"),
    )
    op.create_index(
        op.f("ix_follows_artist_id"), "follows", ["artist_id"], unique=False
    )
    op.create_index(
        op.f("ix_follows_follower_id"), "follows", ["follower_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_follows_follower_id"), table_name="follows")
    op.drop_index(op.f("ix_follows_artist_id"), table_name="follows")
    op.drop_table("follows")
