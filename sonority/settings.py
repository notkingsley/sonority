import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
HASH_ALGORITHM = os.getenv("HASH_ALGORITHM")
ACCESS_TOKEN_EXPIRE_IN = int(os.getenv("ACCESS_TOKEN_EXPIRE_IN"))  # minutes

TRACKS_DIR = Path(os.getenv("TRACKS_DIR"))
