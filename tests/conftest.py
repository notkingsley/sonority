from fastapi.testclient import TestClient
import pytest

from tests.database import TEST_DATABSE_URL, Session
from tests import utils


@pytest.fixture(scope="session")
def test_app():
    """
    Returns a FastAPI test client instance.
    """
    return utils.get_test_app()


@pytest.fixture(scope="session")
def override_db_session(test_app):
    """
    Overrides the database session dependency to use a test database session.
    """
    from sonority.database import get_new_db_session
    from tests.database import get_new_test_db_session

    test_app.dependency_overrides[get_new_db_session] = get_new_test_db_session


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
def raw_client(override_db_session, make_test_tables):
    """
    Returns an unauthenticated test client instance.
    """
    return utils.new_test_client()


@pytest.fixture(scope="function")
def client(raw_client: TestClient):
    """
    Returns an authenticated test client instance.
    """
    return utils.create_test_client(raw_client)


@pytest.fixture(scope="function")
def artist_client(client: TestClient):
    """
    Returns a test client instance authenticated as an artist.
    """
    return utils.create_test_artist_client(client)


@pytest.fixture(scope="function")
def album(session: Session, artist):
    """
    Returns an album
    """
    return utils.create_test_album(session, artist)