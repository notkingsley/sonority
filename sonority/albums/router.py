from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from sonority.albums.dependencies import AlbumById, OwnedAlbumById
from sonority.albums import service
from sonority.albums.schemas import (
    AlbumCreateSchema,
    AlbumOutSchema,
    AlbumUpdateSchema,
    UnreleasedAlbumSchema,
)
from sonority.artists.dependencies import ArtistById, CurrentArtist
from sonority.auth.dependencies import CurrentUser
from sonority.dependencies import Session, Skip, Take, SKIP_DEFAULT, TAKE_DEFAULT


router = APIRouter(prefix="/albums", tags=["albums"])


@router.post(
    "/new", response_model=UnreleasedAlbumSchema, status_code=status.HTTP_201_CREATED
)
def new_album(db: Session, album_schema: AlbumCreateSchema, artist: CurrentArtist):
    """
    Register a new album
    """
    return service.create_album(db, album_schema, artist)


@router.patch("/{album_id}", response_model=UnreleasedAlbumSchema)
def update_album(
    db: Session,
    album: OwnedAlbumById,
    album_schema: AlbumUpdateSchema,
):
    """
    Update an album
    """
    return service.update_album(db, album, album_schema)


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(db: Session, album: OwnedAlbumById):
    """
    Delete an album
    """
    service.delete_album(db, album)


@router.post("/{album_id}/release", response_model=AlbumOutSchema)
def release_album(db: Session, album: OwnedAlbumById):
    """
    Release an album
    """
    return service.release_album(db, album)


@router.get("/drafts", response_model=list[UnreleasedAlbumSchema])
def get_unreleased_albums(
    db: Session,
    artist: CurrentArtist,
    skip: Skip = SKIP_DEFAULT,
    take: Take = TAKE_DEFAULT,
):
    """
    Get all unreleased albums
    """
    return service.get_unreleased_albums(db, artist, skip=skip, take=take)


@router.get("/drafts/{album_id}", response_model=UnreleasedAlbumSchema)
def get_unreleased_album(album: OwnedAlbumById):
    """
    Get an unreleased album by ID

    If the album is released, redirect to the released album
    """
    if album.released:
        return RedirectResponse(f"/albums/{album.id}")

    return album


@router.get("/mine", response_model=list[AlbumOutSchema])
def get_released_albums(
    db: Session,
    artist: CurrentArtist,
    skip: Skip = SKIP_DEFAULT,
    take: Take = TAKE_DEFAULT,
):
    """
    Get all released albums owned by the current artist
    """
    return service.get_released_albums(db, artist, skip=skip, take=take)


@router.get("/{album_id}", response_model=AlbumOutSchema)
def get_album(album: AlbumById, _: CurrentUser):
    """
    Get a released album by ID
    """
    return album


@router.get("/by/{artist_id}", response_model=list[AlbumOutSchema])
def get_albums_by_artist(
    db: Session,
    _: CurrentUser,
    artist: ArtistById,
    skip: Skip = SKIP_DEFAULT,
    take: Take = TAKE_DEFAULT,
):
    """
    Get all albums released by an artist
    """
    return service.get_released_albums(db, artist, skip=skip, take=take)
