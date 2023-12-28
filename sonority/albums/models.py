from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from sonority.database import Base


class Album(Base):
    """
    Model for an album
    """

    __tablename__ = "albums"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False, index=True)
    album_type: Mapped[str] = mapped_column(nullable=False)
    track_count: Mapped[int] = mapped_column(nullable=False, default=0) 
    artist_id: Mapped[UUID] = mapped_column(
        ForeignKey("artists.id"), nullable=False, index=True
    )
    released: Mapped[bool] = mapped_column(nullable=False, default=False)
    release_date: Mapped[date] = mapped_column(nullable=True, default=None)
