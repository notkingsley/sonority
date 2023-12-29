from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from sonority.artists.dependencies import ArtistById, ArtistByIdOrName, CurrentArtist
from sonority.artists import service
from sonority.artists.schemas import (
    ArtistCreateSchema,
    ArtistOutSchema,
    ArtistUpdateSchema,
    GetArtistSchema,
)
from sonority.auth.dependencies import CurrentUser
from sonority.database import Session
from sonority.dependencies import Skip, Take, SKIP_DEFAULT, TAKE_DEFAULT


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

    This doesn't actually do any verification, it just sets the `is_verified`
    """
    return service.verify_artist(db, artist)


@router.get("/", response_model=GetArtistSchema)
def get_artist_by_id_or_name(db: Session, artist: ArtistByIdOrName, user: CurrentUser):
    """
    Get an artist by ID or name
    """
    return {"artist": artist, "is_following": service.follows(db, user, artist)}


@router.post("/{artist_id}/follow")
def follow_artist(
    db: Session,
    artist: ArtistById,
    user: CurrentUser,
) -> dict[Literal["followed"], bool]:
    """
    Follow an artist
    """
    return {"followed": service.follow_artist(db, artist, user)}


@router.post("/{artist_id}/unfollow")
def unfollow_artist(
    db: Session,
    artist: ArtistById,
    user: CurrentUser,
) -> dict[Literal["unfollowed"], bool]:
    """
    Unfollow an artist
    """
    return {"unfollowed": service.unfollow_artist(db, artist, user)}


@router.get("/me/follows", response_model=list[ArtistOutSchema])
def get_followed_artists(
    db: Session,
    user: CurrentUser,
    skip: Skip = SKIP_DEFAULT,
    take: Take = TAKE_DEFAULT,
):
    """
    Get the artists that the current user follows
    """
    return service.get_follows(db, user, skip=skip, take=take)
