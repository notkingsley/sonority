from fastapi import APIRouter, status

from sonority.artists.dependencies import ArtistByIdOrName, CurrentArtist
from sonority.artists import service
from sonority.artists.schemas import (
    ArtistCreateSchema,
    ArtistOutSchema,
    ArtistUpdateSchema,
)
from sonority.auth.dependencies import CurrentUser
from sonority.database import Session


router = APIRouter(prefix="/artists", tags=["artists"])


@router.post(
    "/new", response_model=ArtistOutSchema, status_code=status.HTTP_201_CREATED
)
def new_artist(db: Session, artist_schema: ArtistCreateSchema, user: CurrentUser):
    """
    Register a new artist
    """
    return service.create_artist(db, artist_schema, user)


@router.get("/me", response_model=ArtistOutSchema)
def get_artist(artist: CurrentArtist):
    """
    Get the current user's artist profile
    """
    return artist


@router.patch("/me", response_model=ArtistOutSchema)
def update_artist(
    db: Session,
    artist: CurrentArtist,
    artist_schema: ArtistUpdateSchema,
):
    """
    Update the current user's artist profile
    """
    return service.update_artist(db, artist, artist_schema)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_artist(db: Session, artist: CurrentArtist):
    """
    Delete the current user's artist profile
    """
    service.delete_artist(db, artist)


@router.post("/me/verify", response_model=ArtistOutSchema)
def verify_artist(db: Session, artist: CurrentArtist):
    """
    Verify the current user's artist profile

    This doesn't actually do anything.
    """
    return service.verify_artist(db, artist)


@router.get("/", response_model=ArtistOutSchema)
def get_artist_by_id_or_name(artist: ArtistByIdOrName, _: CurrentUser):
    """
    Get an artist by ID or name
    """
    return artist
