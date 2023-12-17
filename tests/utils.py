import secrets

from fastapi import FastAPI
from fastapi.testclient import TestClient

from sonority.artists.models import Artist
from sonority.artists.schemas import ArtistCreateSchema
from sonority.artists.service import create_artist
from sonority.auth.models import User
from sonority.auth.schemas import UserCreateSchema
from sonority.auth.service import register_user
from tests.database import Session


def create_test_user(session: Session) -> User:
    """
    Create a test user
    """
    user_schema = UserCreateSchema(
        email="testemail@example.com",
        full_name="Test User",
        username="testuser",
        password="testpassword",
    )
    return register_user(session, user_schema)


def create_randomized_test_user(session: Session) -> User:
    """
    Create a randomized test user
    """
    user_schema = UserCreateSchema(
        email=f"{secrets.token_hex(16)}@example.com",
        full_name="Test User",
        username=f"testuser{secrets.token_hex(16)}",
        password="testpassword",
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
    data = {
        "username": "testuser",
        "email": "testemail@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
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
        "username": f"testuser{secrets.token_hex(16)}",
        "email": f"{secrets.token_hex(16)}@example.com",
        "password": "testpassword",
        "full_name": "Test User",
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
    artist_schema = ArtistCreateSchema(
        name="Test Artist",
        description="Test Description",
    )
    return create_artist(session, artist_schema, user)


def create_randomized_test_artist(session: Session, user: User) -> Artist:
    """
    Create a randomized test artist
    """
    artist_schema = ArtistCreateSchema(
        name=f"Test Artist {secrets.token_hex(16)}",
        description=f"Test Description {secrets.token_hex(16)}",
    )
    return create_artist(session, artist_schema, user)


def create_test_artist_client(client: TestClient) -> TestClient:
    """
    Authenticate a test client as an artist
    """
    data = {
        "name": "Test Artist",
        "description": "Test Description",
    }
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
