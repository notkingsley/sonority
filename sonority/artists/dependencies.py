from typing import Annotated
from uuid import UUID

from fastapi import Depends

from sonority.artists.exceptions import ArtistNotFound, BadParameters, DeniedNotArtist
from sonority.artists.models import Artist
from sonority.artists.service import get_artist_by_id, get_artist_by_name
from sonority.auth.dependencies import CurrentUser
from sonority.database import Session


def artist(db: Session, user: CurrentUser):
    """
    Get the current user's artist
    """
    artist = get_artist_by_id(db, user.id)
    if not artist:
        raise DeniedNotArtist("User is not an artist")

    return artist


def artist_or_none_by_id_or_name(db: Session, id: UUID = None, name: str = None):
    """
    Get an artist by id or name or return None if not found
    """
    if id and name or not id and not name:
        raise BadParameters("Only one of id or name can be provided")

    if id:
        return get_artist_by_id(db, id)

    if name:
        return get_artist_by_name(db, name)


def artist_by_id_or_name(
    artist: Annotated[Artist | None, Depends(artist_or_none_by_id_or_name)]
):
    """
    Get an artist by id or name
    """
    if not artist:
        raise ArtistNotFound("Artist not found")

    return artist


ArtistByIdOrName = Annotated[Artist, Depends(artist_by_id_or_name)]

CurrentArtist = Annotated[Artist, Depends(artist)]
