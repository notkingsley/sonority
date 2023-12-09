import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """

    pass


async def get_new_db_session():
    """
    Create a new database session for each request.
    """
    async_session = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
    )
    async with async_session() as session:
        yield session


async def init_db():
    """
    Create all tables in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


DATABASE_URL = os.environ.get("DATABASE_URL")


engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})


Session = Annotated[AsyncSession, Depends(get_new_db_session)]
