import secrets

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