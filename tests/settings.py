import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()

TEST_DATABSE_URL = os.getenv("TEST_DATABSE_URL")

TEST_TRACKS_DIR = Path(os.getenv("TEST_TRACKS_DIR"))
