from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from sonority import settings


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """

    pass


def get_new_db_session():
    """
    Create a new database session for each request.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as session:
        yield session


def init_db(_engine=None, url: str = None):
    """
    Create all tables in the database.
    """
    url = url or settings.DATABASE_URL
    _engine = _engine or create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=_engine)


def drop_db(_engine=None, url: str = None):
    """
    Drop all tables in the database.
    """
    url = url or settings.DATABASE_URL
    _engine = _engine or create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.drop_all(bind=_engine)


engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
