from uuid import UUID

import pytest
from sonority.artists.exceptions import (
    ArtistExists,
    ArtistNameInUse,
    CannotFollowSelf,
    VerifiedArtistIsImmutable,
)
from sonority.artists.models import Artist
from sonority.artists.service import (
    create_artist,
    delete_artist,
    follow_artist,
    follows,
    get_artist_by_id,
    get_artist_by_name,
    get_follows,
    unfollow_artist,
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


def test_follow_artist(session: Session, artist: Artist):
    """
    Test following an artist
    """
    user = create_randomized_test_user(session)
    followed = follow_artist(session, artist, user)
    assert followed is True
    assert follows(session, user, artist) is True


def test_follow_artist_already_following(session: Session, artist: Artist):
    """
    Test following an artist that is already being followed
    """
    user = create_randomized_test_user(session)
    follow_artist(session, artist, user)
    assert follows(session, user, artist) is True

    followed = follow_artist(session, artist, user)
    assert followed is False
    assert follows(session, user, artist) is True


def test_follow_artist_cannot_follow_self(session: Session, artist: Artist, user):
    """
    Test following an artist that is the user
    """
    with pytest.raises(CannotFollowSelf) as exc_info:
        follow_artist(session, artist, user)

    assert exc_info.value.args[0] == "Cannot follow self"
    assert follows(session, user, artist) is False


def test_unfollow_artist(session: Session, artist: Artist):
    """
    Test unfollowing an artist
    """
    user = create_randomized_test_user(session)
    follow_artist(session, artist, user)
    assert follows(session, user, artist) is True

    unfollowed = unfollow_artist(session, artist, user)
    assert unfollowed is True
    assert follows(session, user, artist) is False


def test_unfollow_artist_not_following(session: Session, artist: Artist):
    """
    Test unfollowing an artist that is not being followed
    """
    user = create_randomized_test_user(session)
    assert follows(session, user, artist) is False

    unfollowed = unfollow_artist(session, artist, user)
    assert unfollowed is False
    assert follows(session, user, artist) is False


def test_get_follows(session: Session):
    """
    Test getting follows for a user
    """
    user = create_randomized_test_user(session)
    artist1 = create_randomized_test_artist(session)
    artist2 = create_randomized_test_artist(session)
    artist3 = create_randomized_test_artist(session)
    follow_artist(session, artist1, user)
    follow_artist(session, artist2, user)
    follow_artist(session, artist3, user)

    follows = get_follows(session, user, skip=0, take=20)
    assert len(follows) == 3
    assert artist1 in follows
    assert artist2 in follows
    assert artist3 in follows


def test_get_follows_skip(session: Session):
    """
    Test getting follows for a user with skip
    """
    user = create_randomized_test_user(session)
    artist1 = create_randomized_test_artist(session)
    artist2 = create_randomized_test_artist(session)
    artist3 = create_randomized_test_artist(session)
    follow_artist(session, artist1, user)
    follow_artist(session, artist2, user)
    follow_artist(session, artist3, user)

    follows = get_follows(session, user, skip=1, take=20)
    assert len(follows) == 2
    assert artist1 in follows
    assert artist2 in follows
    assert artist3 not in follows


def test_get_follows_take(session: Session):
    """
    Test getting follows for a user with take
    """
    user = create_randomized_test_user(session)
    artist1 = create_randomized_test_artist(session)
    artist2 = create_randomized_test_artist(session)
    artist3 = create_randomized_test_artist(session)
    follow_artist(session, artist1, user)
    follow_artist(session, artist2, user)
    follow_artist(session, artist3, user)

    follows = get_follows(session, user, skip=0, take=2)
    assert len(follows) == 2
    assert artist1 not in follows
    assert artist2 in follows
    assert artist3 in follows


def test_get_follows_skip_take(session: Session):
    """
    Test getting follows for a user with skip and take
    """
    user = create_randomized_test_user(session)
    artist1 = create_randomized_test_artist(session)
    artist2 = create_randomized_test_artist(session)
    artist3 = create_randomized_test_artist(session)
    follow_artist(session, artist1, user)
    follow_artist(session, artist2, user)
    follow_artist(session, artist3, user)

    follows = get_follows(session, user, skip=1, take=1)
    assert len(follows) == 1
    assert artist1 not in follows
    assert artist2 in follows
    assert artist3 not in follows


def test_get_follows_not_following(session: Session, user):
    """
    Test getting follows for a user that is not following anyone
    """
    follows = get_follows(session, user, skip=0, take=20)
    assert len(follows) == 0


def test_get_follows_skip_too_large(session: Session):
    """
    Test getting follows for a user with skip that is too large
    """
    user = create_randomized_test_user(session)
    artist1 = create_randomized_test_artist(session)
    artist2 = create_randomized_test_artist(session)
    artist3 = create_randomized_test_artist(session)
    follow_artist(session, artist1, user)
    follow_artist(session, artist2, user)
    follow_artist(session, artist3, user)

    follows = get_follows(session, user, skip=3, take=20)
    assert len(follows) == 0


def test_artist_follower_count(session: Session, artist: Artist):
    """
    Test the follower count for an artist
    """
    user1 = create_randomized_test_user(session)
    user2 = create_randomized_test_user(session)
    user3 = create_randomized_test_user(session)
    follow_artist(session, artist, user1)
    follow_artist(session, artist, user2)
    follow_artist(session, artist, user3)

    assert get_artist_by_id(session, artist.id).follower_count == 3