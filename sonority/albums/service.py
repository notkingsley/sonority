from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from sonority.albums.exceptions import (
    AlbumAlreadyReleased,
    AlbumNameInUse,
    ReleasedAlbumIsImmutable,
)
from sonority.albums.models import Album
from sonority.albums.schemas import AlbumCreateSchema, AlbumUpdateSchema
from sonority.artists.models import Artist


def _commit_and_refresh(db: Session, album: Album):
    """
    Commit and refresh an album
    """
    db.commit()
    db.refresh(album)
    return album


def get_album_by_id(db: Session, album_id: UUID):
    """
    Get an album by ID
    """
    return db.execute(select(Album).where(Album.id == album_id)).scalar_one_or_none()


def get_album_by_name(db: Session, name: str):
    """
    Get an album by name
    """
    return db.execute(select(Album).where(Album.name == name)).scalar_one_or_none()


def create_album(db: Session, album_schema: AlbumCreateSchema, artist: Artist):
    """
    Create an album
    """
    if get_album_by_name(db, album_schema.name):
        raise AlbumNameInUse("Album name is already in use")

    album = Album(**album_schema.model_dump(), artist_id=artist.id)
    db.add(album)
    return _commit_and_refresh(db, album)


def update_album(db: Session, album: Album, album_schema: AlbumUpdateSchema):
    """
    Update an album
    """
    if album.released:
        raise ReleasedAlbumIsImmutable("Released albums cannot be modified")

    if not any([album_schema.name, album_schema.album_type]):
        return album

    if album_schema.name and album_schema.name != album.name:
        if get_album_by_name(db, album_schema.name):
            raise AlbumNameInUse("Album name is already in use")

        album.name = album_schema.name

    if album_schema.album_type:
        album.album_type = album_schema.album_type

    return _commit_and_refresh(db, album)


def delete_album(db: Session, album: Album):
    """
    Delete an album
    """
    db.delete(album)
    db.commit()


def release_album(db: Session, album: Album):
    """
    Release an album
    """
    if album.released:
        raise AlbumAlreadyReleased("Album is already released")

    album.released = True
    album.release_date = date.today()
    return _commit_and_refresh(db, album)


def get_all_albums(db: Session, artist: Artist, *, skip: int, take: int):
    """
    Get all albums for an artist
    """
    return (
        db.execute(
            select(Album)
            .where(Album.artist_id == artist.id)
            .order_by(Album.updated_at.desc())
            .offset(skip)
            .limit(take)
        )
        .scalars()
        .all()
    )


def get_released_albums(db: Session, artist: Artist, *, skip: int, take: int):
    """
    Get released albums for an artist
    """
    return (
        db.execute(
            select(Album)
            .where(Album.artist_id == artist.id, Album.released == True)
            .order_by(Album.release_date.desc())
            .offset(skip)
            .limit(take)
        )
        .scalars()
        .all()
    )


def get_unreleased_albums(db: Session, artist: Artist, *, skip: int, take: int):
    """
    Get unreleased albums for an artist
    """
    return (
        db.execute(
            select(Album)
            .where(Album.artist_id == artist.id, Album.released == False)
            .order_by(Album.updated_at.desc())
            .offset(skip)
            .limit(take)
        )
        .scalars()
        .all()
    )
