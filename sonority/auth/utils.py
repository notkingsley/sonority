from datetime import datetime, timedelta
import os
from uuid import UUID

from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel


load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
HASH_ALGORITHM = os.environ.get("HASH_ALGORITHM")
ACCESS_TOKEN_EXPIRE_IN = int(os.environ.get("ACCESS_TOKEN_EXPIRE_IN"))  # minutes


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """
    Data stored in a token
    """

    user_id: UUID


def hash_password(password: str):
    """
    Return the hash of password
    """
    return pwd_context.hash(password)


def verify_password(hash: str, password: str):
    """
    Verify that password matches password

    Return True if the passwords match
    """
    return pwd_context.verify(password, hash)


def decode_token(token: str):
    """
    Decode and validate the contents of token and return the TokenData or None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASH_ALGORITHM])
    except JWTError:
        return None

    sub = payload.get("sub")
    if sub is None:
        return None

    return TokenData(user_id=UUID(sub))


def make_token(token_data: TokenData):
    """
    Make and return a new access token for user with id
    """
    to_encode = {
        "sub": str(token_data.user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_IN),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=HASH_ALGORITHM)
