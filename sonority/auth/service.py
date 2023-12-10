from sqlalchemy import select
from sqlalchemy.orm import Session

from sonority.auth.exceptions import (
    AuthenticationError,
    PasswordChangeError,
    RegistrationError,
    UserUpdateError,
)
from sonority.auth.models import User
from sonority.auth.schemas import (
    UserCreateSchema,
    UserLoginSchema,
    UserPasswordChangeSchema,
    UserUpdateSchema,
)
from sonority.auth.utils import (
    decode_token,
    hash_password,
    make_token,
    TokenData,
    verify_password,
)


def get_user_by_id(db: Session, user_id: int):
    """
    Get a User from the database
    """
    return db.execute(select(User).filter(User.id == user_id)).scalar_one_or_none()


def get_user_by_email(db: Session, email: str):
    """
    Get a User from the database
    """
    return db.execute(select(User).filter(User.email == email)).scalar_one_or_none()


def get_user_by_username(db: Session, username: str):
    """
    Get a User from the database
    """
    return db.execute(
        select(User).filter(User.username == username)
    ).scalar_one_or_none()


def create_user(db: Session, user_schema: UserCreateSchema, pwd_hash: str):
    """
    Create a new User in the database
    """
    user = User(**user_schema.model_dump(exclude=["password"]), pwd_hash=pwd_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def register_user(db: Session, user_schema: UserCreateSchema):
    """
    Register a new user
    """
    if get_user_by_email(db, user_schema.email):
        raise RegistrationError("email already in use")

    if get_user_by_username(db, user_schema.username):
        raise RegistrationError("username already in use")

    pwd_hash = hash_password(user_schema.password)
    return create_user(db, user_schema, pwd_hash)


def update_user(db: Session, user: User, user_schema: UserUpdateSchema):
    """
    Update a User in the database
    """
    if not any([user_schema.email, user_schema.username, user_schema.full_name]):
        return user

    if user_schema.email:
        if user_schema.email != user.email and get_user_by_email(db, user_schema.email):
            raise UserUpdateError("email already in use")

        user.email = user_schema.email

    if user_schema.username:
        if user_schema.username != user.username and get_user_by_username(
            db, user_schema.username
        ):
            raise UserUpdateError("username already in use")

        user.username = user_schema.username

    if user_schema.full_name:
        user.full_name = user_schema.full_name

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User):
    """
    Delete a User from the database
    """
    db.delete(user)
    db.commit()


def change_user_password(
    db: Session, user: User, user_schema: UserPasswordChangeSchema
):
    """
    Change a user's password

    Raise PasswordChangeError if the old password is incorrect
    Returns None otherwise
    """
    if user_schema.old_password == user_schema.new_password:
        raise PasswordChangeError("New password cannot be the same as old password")

    if not verify_password(user.pwd_hash, user_schema.old_password):
        raise PasswordChangeError("Incorrect password")

    user.pwd_hash = hash_password(user_schema.new_password)
    db.commit()


def login_user(db: Session, user_schema: UserLoginSchema):
    """
    Login a user

    Raise AuthenticationError if the user cannot be authenticated
    Returns the user otherwise
    """
    user = get_user_by_email(db, user_schema.email)
    if not user:
        raise AuthenticationError("Email not found")

    if not verify_password(user.pwd_hash, user_schema.password):
        raise AuthenticationError("Incorrect password")

    return user


def auth_token(db: Session, user_schema: UserLoginSchema):
	"""
	Authenticate a user and return a jwt token

	Raise AuthenticationError if the user cannot be authenticated
	Returns the token otherwise
	"""
	user = login_user(db, user_schema)
	return make_token(TokenData(user_id=user.id))


def login_user_from_token(db: Session, token: str):
    """
    Login a user from a jwt token

    Raise AuthenticationError if the user cannot be authenticated
    Returns the user otherwise
    """
    token_data = decode_token(token)
    if not token_data:
        raise AuthenticationError("Invalid token")

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise AuthenticationError("User not found")

    return user
