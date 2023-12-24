from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArtistCreateSchema(BaseModel):
    """
    Schema for creating an artist
    """

    name: str
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class ArtistUpdateSchema(BaseModel):
    """
    Schema for updating an artist
    """

    name: str | None = None
    description: str | None = None


class ArtistOutSchema(ArtistCreateSchema):
    """
    Schema for an artist returned by the API
    """

    id: UUID
    follower_count: int
    is_verified: bool

    model_config = ConfigDict(from_attributes=True, **ArtistCreateSchema.model_config)


class ArtistSchema(ArtistOutSchema):
    """
    Schema for an artist as stored in the database
    """

    pass


class GetArtistSchema(BaseModel):
    """
    Schema for an artist as returned by the API
    """

    artist: ArtistOutSchema
    is_following: bool