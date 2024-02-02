from typing import Annotated
from uuid import UUID

from fastapi import Depends

from sonority.albums.exceptions import AlbumDoesNotExist
from sonority.albums.models import Album
from sonority.albums.service import check_album_owner, get_album_by_id
from sonority.artists.dependencies import CurrentArtist
from sonority.dependencies import Session


def album_by_id(db: Session, album_id: UUID):
    """
    Get an album by ID
    """
    album = get_album_by_id(db, album_id)
    if not album:
        raise AlbumDoesNotExist("Album does not exist")

    return album


def owned_album_by_id(
    album: Annotated[Album, Depends(album_by_id)],
    artist: CurrentArtist,
):
    """
    Get an album by ID that is owned by the current artist
    """
    check_album_owner(album, artist)
    return album


def released_album_by_id(
    album: Annotated[Album, Depends(album_by_id)],
):
    """
    Get a released album by ID
    """
    if not album.released:
        raise AlbumDoesNotExist("Album does not exist")

    return album


AlbumById = Annotated[Album, Depends(released_album_by_id)]
OwnedAlbumById = Annotated[Album, Depends(owned_album_by_id)]
