from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from sonority.artists.exceptions import (
    ArtistExists,
    ArtistNameInUse,
    CannotFollowSelf,
    VerifiedArtistIsImmutable,
)
from sonority.artists.models import Artist, Follow
from sonority.artists.schemas import ArtistCreateSchema, ArtistUpdateSchema
from sonority.auth.models import User


def _get_artist(db: Session, column, value):
    """
    Get an Artist from the database with the condition column == value
    """
    row = db.execute(
        select(Artist, func.count(Follow.follower_id))
        .join(Follow, isouter=True)
        .where(column == value)
    ).one_or_none()
    if not row:
        return None

    artist, follower_count = row._tuple()
    if artist:
        artist.follower_count = follower_count

    return artist


def _update_follower_count(db: Session, artist: Artist):
    """
    Update the follower count for an artist
    """
    artist.follower_count = db.execute(
        select(func.count(Follow.follower_id)).where(Follow.artist_id == artist.id)
    ).scalar_one()


def _commit_and_refresh(db: Session, artist: Artist):
    """
    Commit and refresh an artist
    """
    db.commit()
    db.refresh(artist)
    _update_follower_count(db, artist)
    return artist


def artist_exists_by_id(db: Session, artist_id: UUID):
    """
    Check if an Artist exists in the database
    """
    return bool(
        db.execute(select(Artist.id).where(Artist.id == artist_id)).scalar_one_or_none()
    )


def artist_exists_by_name(db: Session, name: str):
    """
    Check if an Artist exists in the database
    """
    return bool(
        db.execute(select(Artist.id).where(Artist.name == name)).scalar_one_or_none()
    )


def get_artist_by_id(db: Session, artist_id: UUID):
    """
    Get an Artist from the database
    """
    return _get_artist(db, Artist.id, artist_id)


def get_artist_by_name(db: Session, name: str):
    """
    Get an Artist from the database
    """
    return _get_artist(db, Artist.name, name)


def create_artist(db: Session, schema: ArtistCreateSchema, user: User):
    """
    Create a new Artist in the database
    """
    if artist_exists_by_id(db, user.id):
        raise ArtistExists("Artist already exists")

    if artist_exists_by_name(db, schema.name):
        raise ArtistNameInUse("Artist name is already in use")

    artist = Artist(**schema.model_dump(), id=user.id)
    db.add(artist)
    return _commit_and_refresh(db, artist)


def update_artist(db: Session, artist: Artist, schema: ArtistUpdateSchema):
    """
    Update an Artist in the database
    """
    if not any([schema.name, schema.description]):
        return artist

    if schema.name and schema.name != artist.name:
        if artist.is_verified:
            raise VerifiedArtistIsImmutable("Cannot change name of verified artist")

        if artist_exists_by_name(db, schema.name):
            raise ArtistNameInUse("Artist name is already in use")

        artist.name = schema.name

    if schema.description:
        artist.description = schema.description

    return _commit_and_refresh(db, artist)


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
    return _commit_and_refresh(db, artist)


def _get_follow(db: Session, artist_id: UUID, follower_id: UUID):
    """
    Get a Follow from the database
    """
    return db.execute(
        select(Follow).where(
            Follow.artist_id == artist_id, Follow.follower_id == follower_id
        )
    ).scalar_one_or_none()


def follows(db: Session, user: User, artist: Artist):
    """
    Check if a user is following an artist

    Returns True if the user is following the artist, False otherwise.
    """
    return bool(_get_follow(db, artist.id, user.id))


def follow_artist(db: Session, artist: Artist, user: User):
    """
    Follow an Artist

    Returns True if the artist was followed, False otherwise.
    """
    if artist.id == user.id:
        raise CannotFollowSelf("Cannot follow self")

    if follows(db, user, artist):
        return False

    follow = Follow(artist_id=artist.id, follower_id=user.id)
    db.add(follow)
    db.commit()
    return True


def unfollow_artist(db: Session, artist: Artist, user: User):
    """
    Unfollow an Artist

    Returns True if the artist was unfollowed, False otherwise.
    """
    follow = _get_follow(db, artist.id, user.id)
    if not follow:
        return False

    db.delete(follow)
    db.commit()
    return True


def get_follows(db: Session, user: User, *, skip: int, take: int):
    """
    Get a list of artists that a user is following
    """
    return (
        db.execute(
            select(Artist)
            .join(Follow)
            .where(Follow.follower_id == user.id)
            .order_by(Follow.created_at.desc())
            .offset(skip)
            .limit(take)
        )
        .scalars()
        .all()
    )
