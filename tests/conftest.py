from fastapi.testclient import TestClient
import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database

from sonority.database import drop_db, init_db
from tests.database import TEST_DATABSE_URL, Session



@pytest.fixture(scope="session", autouse=True)
def make_test_db():
    """
    Create a clean database on each test run.
    """
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


@pytest.fixture(scope= "session")
def override_db_session(testapp):
    from sonority.database import get_new_db_session
    from tests.database import get_new_test_db_session
    testapp.dependency_overrides[get_new_db_session] = get_new_test_db_session


@pytest.fixture(scope="function")
def client(testapp, override_db_session, make_test_tables):
    return TestClient(testapp)