import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLAlchemySession
from sqlalchemy.orm import DeclarativeBase


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


def init_db():
    """
    Create all tables in the database.
    """
    Base.metadata.create_all(bind=engine)


DATABASE_URL = os.environ.get("DATABASE_URL")


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


Session = Annotated[SQLAlchemySession, Depends(get_new_db_session)]
