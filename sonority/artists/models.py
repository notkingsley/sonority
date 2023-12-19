from datetime import datetime
from typing import ClassVar
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from sonority.database import Base


class Artist(Base):
    """
    Model for an artist
    """

    __tablename__ = "artists"

    id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    follower_count: ClassVar[int]


class Follow(Base):
    """
    Model for a follow
    """

    __tablename__ = "follows"

    follower_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), primary_key=True, index=True
    )
    artist_id: Mapped[UUID] = mapped_column(
        ForeignKey("artists.id"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
