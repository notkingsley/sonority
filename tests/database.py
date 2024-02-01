from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests import settings


def get_new_test_db_session():
    with Session() as session:
        yield session


engine = create_engine(settings.TEST_DATABSE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
