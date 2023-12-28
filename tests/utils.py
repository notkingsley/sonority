import secrets

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sonority.albums.models import Album
from sonority.albums.schemas import AlbumCreateSchema
from sonority.albums.service import create_album
from sonority.artists.models import Artist
from sonority.artists.schemas import ArtistCreateSchema
from sonority.artists.service import create_artist
from sonority.auth.models import User
from sonority.auth.schemas import UserCreateSchema
from sonority.auth.service import register_user
from tests.database import Session


class Anything:
    """
    A class that will match any value
    """

    def __eq__(self, other):
        return True


anything = Anything()


_BASE_DEFAULT_USER_INFO = {
    "username": "testuser",
    "email": "testemail@example.com",
    "full_name": "Test User",
}

DEFAULT_USER_INFO = {
    "id": anything,
    "created_at": anything,
    "updated_at": anything,
    **_BASE_DEFAULT_USER_INFO,
}

DEFAULT_USER_CREATE_INFO = {
    "password": "testpassword",
    **_BASE_DEFAULT_USER_INFO,
}

DEFAULT_ARTIST_CREATE_INFO = {
    "name": "Test Artist",
    "description": "Test Description",
}

DEFAULT_ARTIST_INFO = {
    "id": anything,
    "is_verified": False,
    "follower_count": 0,
    **DEFAULT_ARTIST_CREATE_INFO,
}

DEFAULT_ALBUM_CREATE_INFO = {
    "name": "Test Album",
    "album_type": "album",
}


def create_test_user(session: Session) -> User:
    """
    Create a test user
    """
    user_schema = UserCreateSchema(**DEFAULT_USER_CREATE_INFO)
    return register_user(session, user_schema)


def create_randomized_test_user(session: Session) -> User:
    """
    Create a randomized test user
    """
    user_schema = UserCreateSchema(
        email=f"email{secrets.token_hex(16)}@example.com",
        username=f"testuser{secrets.token_hex(16)}",
        password=DEFAULT_USER_CREATE_INFO["password"],
        full_name=f"Test User {secrets.token_hex(16)}",
    )
    return register_user(session, user_schema)


def get_test_app() -> FastAPI:
    """
    Return a new test app
    """
    from sonority.server import app

    return app


def new_test_client():
    """
    Return a new test client
    """
    return TestClient(get_test_app())


def create_test_client(client: TestClient | None = None) -> TestClient:
    """
    Authenticate a test client
    """
    client = client or new_test_client()
    data = {**DEFAULT_USER_CREATE_INFO}
    client.post("/users/register", json=data)

    response = client.post(
        "/users/login", data={"username": data["email"], "password": data["password"]}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


def create_randomized_test_client() -> TestClient:
    """
    Authenticate a test client as a randomized user
    """
    client = new_test_client()
    data = {
        **DEFAULT_USER_CREATE_INFO,
        "username": f"testuser{secrets.token_hex(16)}",
        "email": f"email{secrets.token_hex(16)}@example.com",
    }
    client.post("/users/register", json=data)

    response = client.post(
        "/users/login", data={"username": data["email"], "password": data["password"]}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


def create_test_artist(session: Session, user: User) -> Artist:
    """
    Create a test artist
    """
    artist_schema = ArtistCreateSchema(**DEFAULT_ARTIST_CREATE_INFO)
    return create_artist(session, artist_schema, user)


def create_randomized_test_artist(session: Session, user: User | None = None) -> Artist:
    """
    Create a randomized test artist
    """
    user = user or create_randomized_test_user(session)
    artist_schema = ArtistCreateSchema(
        name=f"Test Artist {secrets.token_hex(16)}",
        description=f"Test Description {secrets.token_hex(16)}",
    )
    return create_artist(session, artist_schema, user)


def create_test_artist_client(client: TestClient) -> TestClient:
    """
    Authenticate a test client as an artist
    """
    data = {**DEFAULT_ARTIST_CREATE_INFO}
    client.post("/artists/new", json=data)

    return client


def create_randomized_test_artist_client() -> TestClient:
    """
    Authenticate a test client as a randomized artist
    """
    client = create_randomized_test_client()
    data = {
        "name": f"Test Artist {secrets.token_hex(16)}",
        "description": f"Test Description {secrets.token_hex(16)}",
    }
    client.post("/artists/new", json=data)

    return client


def create_test_album(session: Session, artist: Artist) -> Album:
    """
    Create a test album
    """
    album_schema = AlbumCreateSchema(**DEFAULT_ALBUM_CREATE_INFO)
    return create_album(session, album_schema, artist)


def create_randomized_test_album(session: Session, artist: Artist) -> Album:
    """
    Create a randomized test album
    """
    album_schema = AlbumCreateSchema(
        name=f"Test Album {secrets.token_hex(16)}",
        album_type="album",
    )
    return create_album(session, album_schema, artist)
