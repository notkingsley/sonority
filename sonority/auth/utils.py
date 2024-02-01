from datetime import datetime, timedelta
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from sonority import settings


class TokenData(BaseModel):
    """
    Data stored in a token
    """

    user_id: UUID


def hash_password(password: str):
    """
    Return the hash of password
    """
    context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return context.hash(password)


def verify_password(hash: str, password: str):
    """
    Verify that password matches password

    Return True if the passwords match
    """
    context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return context.verify(password, hash)


def decode_token(token: str):
    """
    Decode and validate the contents of token and return the TokenData or None
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM]
        )
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
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_IN),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.HASH_ALGORITHM)
