from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from sonority.artists.exceptions import (
    ArtistExists,
    ArtistNameInUse,
    VerifiedArtistIsImmutable,
)
from sonority.artists.models import Artist
from sonority.artists.schemas import ArtistCreateSchema, ArtistUpdateSchema
from sonority.auth.models import User


def get_artist_by_id(db: Session, artist_id: UUID):
    """
    Get an Artist from the database
    """
    return db.execute(
        select(Artist).filter(Artist.id == artist_id)
    ).scalar_one_or_none()


def get_artist_by_name(db: Session, name: str):
    """
    Get an Artist from the database
    """
    return db.execute(select(Artist).filter(Artist.name == name)).scalar_one_or_none()


def create_artist(db: Session, schema: ArtistCreateSchema, user: User):
    """
    Create a new Artist in the database
    """
    if get_artist_by_id(db, user.id):
        raise ArtistExists("Artist already exists")

    if get_artist_by_name(db, schema.name):
        raise ArtistNameInUse("Artist name is already in use")    

    artist = Artist(**schema.model_dump(), id=user.id)
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


def update_artist(db: Session, artist: Artist, schema: ArtistUpdateSchema):
    """
    Update an Artist in the database
    """
    if not any([schema.name, schema.description]):
        return artist

    if schema.name and schema.name != artist.name:
        if artist.is_verified:
            raise VerifiedArtistIsImmutable("Cannot change name of verified artist")

        if get_artist_by_name(db, schema.name):
            raise ArtistNameInUse("Artist name is already in use")

        artist.name = schema.name

    if schema.description:
        artist.description = schema.description

    db.commit()
    db.refresh(artist)
    return artist


def delete_artist(db: Session, artist: Artist):
    """
    Delete an Artist from the database
    """
    db.delete(artist)
    db.commit()


def verify_artist(db: Session, artist: Artist):
    """
    Verify an Artist
    """
    if artist.is_verified:
        raise VerifiedArtistIsImmutable("Artist is already verified")

    artist.is_verified = True
    db.commit()
    db.refresh(artist)
    return artist
