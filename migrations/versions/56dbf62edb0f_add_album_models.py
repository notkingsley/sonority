"""add Album models

Revision ID: 56dbf62edb0f
Revises: 27814322ada1
Create Date: 2024-01-13 00:20:24.813678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "56dbf62edb0f"
down_revision: Union[str, None] = "27814322ada1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "albums",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("album_type", sa.String(), nullable=False),
        sa.Column("track_count", sa.Integer(), nullable=False),
        sa.Column("artist_id", sa.Uuid(), nullable=False),
        sa.Column("released", sa.Boolean(), nullable=False),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artists.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "artist_id", name="uq_album_name_artist_id"),
    )
    op.create_index(op.f("ix_albums_artist_id"), "albums", ["artist_id"], unique=False)
    op.create_index(op.f("ix_albums_name"), "albums", ["name"], unique=False)
    op.create_table(
        "album_likes",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("album_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["albums.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "album_id"),
    )
    op.create_index(
        op.f("ix_album_likes_album_id"), "album_likes", ["album_id"], unique=False
    )
    op.create_index(
        op.f("ix_album_likes_user_id"), "album_likes", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_album_likes_user_id"), table_name="album_likes")
    op.drop_index(op.f("ix_album_likes_album_id"), table_name="album_likes")
    op.drop_table("album_likes")
    op.drop_index(op.f("ix_albums_name"), table_name="albums")
    op.drop_index(op.f("ix_albums_artist_id"), table_name="albums")
    op.drop_table("albums")
