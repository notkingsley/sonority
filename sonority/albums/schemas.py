from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AlbumCreateSchema(BaseModel):
    """
    Schema for creating an album
    """

    name: str
    album_type: Literal["album", "single"]

    model_config = ConfigDict(extra="forbid")


class AlbumUpdateSchema(BaseModel):
    """
    Schema for updating an album
    """

    name: str | None = None
    album_type: Literal["album", "single"] | None = None


class UnreleasedAlbumSchema(AlbumCreateSchema):
    """
    Schema for an unreleased album
    """

    id: UUID
    track_count: int
    artist_id: UUID

    model_config = ConfigDict(from_attributes=True, **AlbumCreateSchema.model_config)


class AlbumOutSchema(UnreleasedAlbumSchema):
    """
    Schema for an album returned by the API
    """

    release_date: date


class AlbumSchema(AlbumOutSchema):
    """
    Schema for an album as stored in the database
    """

    released: bool
