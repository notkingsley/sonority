import pytest
from sonority.albums.exceptions import (
    AlbumAlreadyReleased,
    AlbumNameInUse,
    ReleasedAlbumIsImmutable,
)
from sonority.albums.models import Album
from sonority.albums.schemas import AlbumCreateSchema, AlbumUpdateSchema
from sonority.albums.service import (
    create_album,
    delete_album,
    get_album_by_id,
    get_album_by_name,
    get_all_albums,
    get_released_albums,
    get_unreleased_albums,
    release_album,
    update_album,
)
from sonority.artists.models import Artist
from sonority.database import Session
from tests.utils import DEFAULT_ALBUM_CREATE_INFO, create_randomized_test_album


def test_create_album(session: Session, artist: Artist):
    """
    Test creating an album
    """
    album_schema = AlbumCreateSchema(**DEFAULT_ALBUM_CREATE_INFO)
    album = create_album(session, album_schema, artist)
    assert album.name == album_schema.name
    assert album.album_type == album_schema.album_type
    assert album.artist_id == artist.id
    assert album.released is False
    assert album.release_date is None
    assert album.track_count == 0

    album = get_album_by_id(session, album.id)
    assert album.name == album_schema.name
    assert album.album_type == album_schema.album_type
    assert album.artist_id == artist.id
    assert album.released is False
    assert album.release_date is None
    assert album.track_count == 0


def test_create_album_name_in_use(session: Session, artist: Artist, album: Album):
    """
    Test creating an album with a name that is already in use
    """
    album_schema = AlbumCreateSchema(**DEFAULT_ALBUM_CREATE_INFO)
    with pytest.raises(AlbumNameInUse) as exc_info:
        create_album(session, album_schema, artist)

    assert exc_info.value.args[0] == "Album name is already in use"


def test_update_album_name(session: Session, album: Album):
    """
    Test updating an album with a new name
    """
    album_schema = AlbumUpdateSchema(name="New Name")
    album = update_album(session, album, album_schema)
    assert album.name == album_schema.name


def test_update_album_name_in_use(session: Session, album: Album, artist: Artist):
    """
    Test updating an album with a name that is already in use
    """
    album2 = create_randomized_test_album(session, artist)
    album_schema = AlbumUpdateSchema(name=album2.name)
    with pytest.raises(AlbumNameInUse) as exc_info:
        update_album(session, album, album_schema)

    assert exc_info.value.args[0] == "Album name is already in use"


def test_update_album_type(session: Session, album: Album):
    """
    Test updating an album with a new type
    """
    album_schema = AlbumUpdateSchema(album_type="single")
    album = update_album(session, album, album_schema)
    assert album.album_type == album_schema.album_type

    album = get_album_by_id(session, album.id)
    assert album.album_type == album_schema.album_type


def test_update_album_released(session: Session, album: Album):
    """
    Test updating a released album
    """
    release_album(session, album)
    album_schema = AlbumUpdateSchema(name="New Name")
    with pytest.raises(ReleasedAlbumIsImmutable) as exc_info:
        update_album(session, album, album_schema)

    assert exc_info.value.args[0] == "Released albums cannot be modified"


def test_update_album_no_changes(session: Session, album: Album):
    """
    Test updating an album with no changes
    """
    album_schema = AlbumUpdateSchema()
    db_album = update_album(session, album, album_schema)
    assert db_album == album


def test_delete_album(session: Session, album: Album):
    """
    Test deleting an album
    """
    delete_album(session, album)
    assert get_album_by_id(session, album.id) is None


def test_release_album(session: Session, album: Album):
    """
    Test releasing an album
    """
    album = release_album(session, album)
    assert album.released is True
    assert album.release_date is not None

    album = get_album_by_id(session, album.id)
    assert album.released is True
    assert album.release_date is not None


def test_release_album_already_released(session: Session, album: Album):
    """
    Test releasing an album that is already released
    """
    release_album(session, album)
    with pytest.raises(AlbumAlreadyReleased) as exc_info:
        release_album(session, album)

    assert exc_info.value.args[0] == "Album is already released"


def test_get_album_by_name(session: Session, album: Album):
    """
    Test getting an album by name
    """
    assert get_album_by_name(session, album.name) == album


def test_get_all_albums(session: Session, album: Album, artist: Artist):
    """
    Test getting all albums
    """
    album2 = create_randomized_test_album(session, artist)
    album3 = create_randomized_test_album(session, artist)
    album4 = create_randomized_test_album(session, artist)
    release_album(session, album)
    release_album(session, album3)

    albums = get_all_albums(session, artist, skip=0, take=10)
    assert set(albums) == {album, album2, album3, album4}


def test_get_released_albums(session: Session, album: Album, artist: Artist):
    """
    Test getting released albums
    """
    album2 = create_randomized_test_album(session, artist)
    album3 = create_randomized_test_album(session, artist)
    album4 = create_randomized_test_album(session, artist)
    release_album(session, album)
    release_album(session, album3)

    albums = get_released_albums(session, artist, skip=0, take=10)
    assert set(albums) == {album, album3}


def test_get_unreleased_albums(session: Session, album: Album, artist: Artist):
    """
    Test getting unreleased albums
    """
    album2 = create_randomized_test_album(session, artist)
    album3 = create_randomized_test_album(session, artist)
    album4 = create_randomized_test_album(session, artist)
    release_album(session, album)
    release_album(session, album3)

    albums = get_unreleased_albums(session, artist, skip=0, take=10)
    assert set(albums) == {album2, album4}