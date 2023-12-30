from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from sonority.database import Base


class Album(Base):
    """
    Model for an album
    """

    __tablename__ = "albums"
    __table_args__ = (
        UniqueConstraint("name", "artist_id", name="uq_album_name_artist_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    album_type: Mapped[str] = mapped_column(nullable=False)
    track_count: Mapped[int] = mapped_column(nullable=False, default=0)
    artist_id: Mapped[UUID] = mapped_column(
        ForeignKey("artists.id"), nullable=False, index=True
    )
    released: Mapped[bool] = mapped_column(nullable=False, default=False)
    release_date: Mapped[date] = mapped_column(nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
