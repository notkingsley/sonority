import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_new_test_db_session():
	with Session() as session:
		yield session


load_dotenv()

TEST_DATABSE_URL = os.environ.get("TEST_DATABSE_URL")

engine = create_engine(TEST_DATABSE_URL, connect_args={"check_same_thread": False})

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
