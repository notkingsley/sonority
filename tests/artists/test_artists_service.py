from uuid import UUID

import pytest
from sonority.artists.exceptions import (
    ArtistExists,
    ArtistNameInUse,
    VerifiedArtistIsImmutable,
)
from sonority.artists.models import Artist
from sonority.artists.service import (
    create_artist,
    delete_artist,
    get_artist_by_id,
    get_artist_by_name,
    update_artist,
    verify_artist,
)
from sonority.artists.schemas import ArtistCreateSchema, ArtistUpdateSchema
from tests.database import Session
from tests.utils import (
    create_randomized_test_artist,
    create_randomized_test_user,
)


def test_create_artist(session: Session, user):
    """
    Test creating an artist
    """
    artist_schema = ArtistCreateSchema(
        name="Test Artist",
        description="Test Description",
    )
    artist = create_artist(session, artist_schema, user)
    assert artist.id == user.id
    assert artist.name == artist_schema.name
    assert artist.description == artist_schema.description

    db_artist = get_artist_by_id(session, user.id)
    assert db_artist.id == user.id
    assert db_artist.name == artist_schema.name
    assert db_artist.description == artist_schema.description


def test_create_artist_already_exists(session: Session, artist: Artist, user):
    """
    Test creating an artist that already exists
    """
    artist_schema = ArtistCreateSchema(
        name="Test Artist 2",
        description="Test Description 2",
    )
    with pytest.raises(ArtistExists) as exc_info:
        create_artist(session, artist_schema, user)

    assert exc_info.value.args[0] == "Artist already exists"


def test_create_artist_name_in_use(session: Session, artist: Artist):
    """
    Test creating an artist with a name that is already in use
    """
    user2 = create_randomized_test_user(session)
    artist_schema = ArtistCreateSchema(
        name="Test Artist",
        description="Test Description 2",
    )
    with pytest.raises(ArtistNameInUse) as exc_info:
        create_artist(session, artist_schema, user2)

    assert exc_info.value.args[0] == "Artist name is already in use"


def test_get_artist_by_id(session: Session, artist: Artist):
    """
    Test getting an artist by ID
    """
    db_artist = get_artist_by_id(session, artist.id)
    assert db_artist
    assert db_artist.id == artist.id
    assert db_artist.name == artist.name
    assert db_artist.description == artist.description


def test_get_artist_by_id_not_found(session: Session):
    """
    Test getting an artist by ID that does not exist
    """
    db_artist = get_artist_by_id(session, UUID("00000000-0000-0000-0000-000000000000"))
    assert not db_artist


def test_get_artist_by_name(session: Session, artist: Artist):
    """
    Test getting an artist by name
    """
    db_artist = get_artist_by_name(session, artist.name)
    assert db_artist
    assert db_artist.id == artist.id
    assert db_artist.name == artist.name
    assert db_artist.description == artist.description


def test_get_artist_by_name_not_found(session: Session):
    """
    Test getting an artist by name that does not exist
    """
    db_artist = get_artist_by_name(session, "Bad Test Artist")
    assert not db_artist


def test_update_artist(session: Session, artist: Artist):
    """
    Test updating an artist
    """
    artist_schema = ArtistUpdateSchema(
        name="Test Artist 2",
        description="Test Description 2",
    )
    artist = update_artist(session, artist, artist_schema)
    assert artist.name == artist_schema.name
    assert artist.description == artist_schema.description

    db_artist = get_artist_by_id(session, artist.id)
    assert db_artist.name == artist_schema.name
    assert db_artist.description == artist_schema.description


def test_update_artist_name_in_use(session: Session, artist: Artist):
    """
    Test updating an artist with a name that is already in use
    """
    user2 = create_randomized_test_user(session)
    artist2 = create_randomized_test_artist(session, user2)
    artist_schema = ArtistUpdateSchema(
        name=artist2.name,
    )
    with pytest.raises(ArtistNameInUse) as exc_info:
        update_artist(session, artist, artist_schema)

    assert exc_info.value.args[0] == "Artist name is already in use"


def test_update_artist_name_verified(session: Session, artist: Artist):
    """
    Test updating an artist's name that is verified
    """
    verify_artist(session, artist)
    artist_schema = ArtistUpdateSchema(
        name="Test Artist 2",
    )
    with pytest.raises(VerifiedArtistIsImmutable) as exc_info:
        update_artist(session, artist, artist_schema)

    assert exc_info.value.args[0] == "Cannot change name of verified artist"


def test_update_artist_no_changes(session: Session, artist: Artist):
    """
    Test updating an artist with no changes
    """
    artist_schema = ArtistUpdateSchema()
    updated_artist = update_artist(session, artist, artist_schema)
    assert updated_artist is artist

    db_artist = get_artist_by_id(session, artist.id)
    assert db_artist.name == artist.name
    assert db_artist.description == artist.description


def test_delete_artist(session: Session, artist: Artist):
    """
    Test deleting an artist
    """
    artist_id = artist.id
    delete_artist(session, artist)
    assert get_artist_by_id(session, artist_id) is None


def test_verify_artist(session: Session, artist: Artist):
    """
    Test verifying an artist
    """
    artist = verify_artist(session, artist)
    assert artist.is_verified

    db_artist = get_artist_by_id(session, artist.id)
    assert db_artist.is_verified


def test_verify_artist_already_verified(session: Session, artist: Artist):
    """
    Test verifying an artist that is already verified
    """
    verify_artist(session, artist)
    with pytest.raises(VerifiedArtistIsImmutable) as exc_info:
        verify_artist(session, artist)

    assert exc_info.value.args[0] == "Artist is already verified"
