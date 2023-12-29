from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from sonority.auth.models import User
from sonority.auth.service import login_user_from_token
from sonority.dependencies import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def current_user(db: Session, token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Get the current user from a jwt token in the Authorization header
    """
    return login_user_from_token(db, token)


CurrentUser = Annotated[User, Depends(current_user)]
