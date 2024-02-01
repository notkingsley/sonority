from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from sonority.albums.exceptions import (
    AlbumAlreadyReleased,
    AlbumNameInUse,
    ReleasedAlbumIsImmutable,
)
from sonority.albums.models import Album, Likes
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


def has_album_by_name(db: Session, name: str, artist_id: UUID):
    """
    Check if an album exists by name for an artist
    """
    return bool(
        db.execute(
            select(Album.id).where(Album.name == name, Album.artist_id == artist_id)
        ).scalar_one_or_none()
    )


def create_album(db: Session, album_schema: AlbumCreateSchema, artist: Artist):
    """
    Create an album
    """
    if has_album_by_name(db, album_schema.name, artist.id):
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
        if has_album_by_name(db, album_schema.name, album.artist_id):
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
            .where(Album.artist_id == artist.id, Album.released == True)  # noqa
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
            .where(Album.artist_id == artist.id, Album.released == False)  # noqa
            .order_by(Album.updated_at.desc())
            .offset(skip)
            .limit(take)
        )
        .scalars()
        .all()
    )


def _get_like(db: Session, album_id: UUID, user_id: UUID):
    """
    Get a like for an album by a user
    """
    return db.execute(
        select(Likes).where(Likes.album_id == album_id, Likes.user_id == user_id)
    ).scalar_one_or_none()


def likes(db: Session, album: Album, user_id: UUID):
    """
    Check if a user likes an album
    """
    return _get_like(db, album.id, user_id) is not None


def like_album(db: Session, album: Album, user_id: UUID):
    """
    Like an album
    """
    if likes(db, album, user_id):
        return False

    like = Likes(album_id=album.id, user_id=user_id)
    db.add(like)
    db.commit()
    return True


def unlike_album(db: Session, album: Album, user_id: UUID):
    """
    Unlike an album
    """
    like = _get_like(db, album.id, user_id)
    if not like:
        return False

    db.delete(like)
    db.commit()
    return True


def get_liked_albums(db: Session, user_id: UUID, *, skip: int, take: int):
    """
    Get a list of albums that a user likes
    """
    return (
        db.execute(
            select(Album)
            .join(Likes, Album.id == Likes.album_id)
            .where(Likes.user_id == user_id)
            .order_by(Likes.created_at.desc())
            .offset(skip)
            .limit(take)
        )
        .scalars()
        .all()
    )
