from fastapi.testclient import TestClient
import pytest

from tests.database import TEST_DATABSE_URL, Session
from tests import utils


@pytest.fixture(scope="session", autouse=True)
def make_test_db():
	"""
	Create a clean database on each test run.
	"""
	from sqlalchemy_utils import create_database, database_exists, drop_database

	if database_exists(TEST_DATABSE_URL):
		drop_database(TEST_DATABSE_URL)
	create_database(TEST_DATABSE_URL)
	yield
	drop_database(TEST_DATABSE_URL)


@pytest.fixture(scope="function", autouse=True)
def make_test_tables(make_test_db: None):
	"""
	Create clean database tables on each test run.
	"""
	from sonority.database import drop_db, init_db

	init_db(url=TEST_DATABSE_URL)
	yield
	drop_db(url=TEST_DATABSE_URL)


@pytest.fixture(scope="function")
def session(make_test_tables: None):
	"""
	Creates a new database session with (with working transaction)
	for test duration.
	"""
	with Session() as session:
		yield session


@pytest.fixture(scope="session")
def testapp():
	"""
	Returns a FastAPI test client instance.
	"""
	from sonority.server import app

	yield app


@pytest.fixture(scope="session")
def override_db_session(testapp):
	"""
	Overrides the database session dependency to use a test database session.
	"""
	from sonority.database import get_new_db_session
	from tests.database import get_new_test_db_session

	testapp.dependency_overrides[get_new_db_session] = get_new_test_db_session


@pytest.fixture(scope="function")
def registered_user(session: Session):
	"""
	Return a registered user
	"""
	return utils.create_test_user(session)


@pytest.fixture(scope="function")
def user(session: Session):
	"""
	Return a registered user
	"""
	return utils.create_test_user(session)


@pytest.fixture(scope="function")
def artist(session: Session, user):
	"""
	Return an artist
	"""
	return utils.create_test_artist(session, user)


@pytest.fixture(scope="function")
def raw_client(testapp, override_db_session, make_test_tables):
	"""
	Returns an unauthenticated test client instance.
	"""
	yield TestClient(testapp)


@pytest.fixture(scope="function")
def client(raw_client: TestClient):
	"""
	Returns an authenticated test client instance.
	"""
	data = {
		"username": "testuser",
		"email": "testemail@example.com",
		"password": "testpassword",
		"full_name": "Test User",
	}
	raw_client.post("/users/register", json=data)

	response = raw_client.post(
		"/users/login", data={"username": data["email"], "password": data["password"]}
	)
	token = response.json()["access_token"]
	raw_client.headers.update({"Authorization": f"Bearer {token}"})

	yield raw_client