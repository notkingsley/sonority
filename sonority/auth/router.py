from typing import Annotated, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ValidationError

from sonority.auth.dependencies import CurrentUser
from sonority.auth.schemas import (
    UserCreateSchema,
    UserLoginSchema,
    UserOutSchema,
    UserPasswordChangeSchema,
    UserUpdateSchema,
)
from sonority.auth.service import (
    auth_token,
    change_user_password,
    delete_user,
    get_user_by_id,
    register_user,
    update_user,
)
from sonority.database import Session


router = APIRouter(prefix="/users", tags=["users"])


class LoginToken(BaseModel):
    """
    A Token as returned from the /login endpoint
    """

    access_token: str
    token_type: str


@router.post(
    "/register", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED
)
def register(db: Session, user_schema: UserCreateSchema):
    """
    Register a new user
    """
    return register_user(db, user_schema)


@router.post("/login", response_model=LoginToken)
def login(db: Session, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Log in a user
    """
    try:
        user_schema = UserLoginSchema(
            email=form_data.username, password=form_data.password
        )
    except ValidationError as e:
        raise RequestValidationError(e.errors()) from e

    return {
        "access_token": auth_token(db, user_schema),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserOutSchema)
def me(user: CurrentUser):
    """
    Get the current user
    """
    return user


@router.patch("/me", response_model=UserOutSchema)
def update_me(db: Session, user: CurrentUser, user_schema: UserUpdateSchema):
    """
    Update the current user
    """
    return update_user(db, user, user_schema)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(db: Session, user: CurrentUser):
    """
    Delete the current user
    """
    delete_user(db, user)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    db: Session, user: CurrentUser, user_schema: UserPasswordChangeSchema
):
    """
    Change the current user's password
    """
    change_user_password(db, user, user_schema)


@router.get("/{user_id}", response_model=Union[UserOutSchema, None])
def get_user(db: Session, user_id: UUID):
    """
    Get a user by id
    """
    user = get_user_by_id(db, user_id)
    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
