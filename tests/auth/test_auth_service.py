from uuid import UUID

import pytest
from sonority.auth.exceptions import (
    AuthenticationError,
    PasswordChangeError,
    RegistrationError,
    UserUpdateError,
)
from sonority.auth.models import User
from sonority.auth.service import (
    auth_token,
    change_user_password,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    login_user,
    login_user_from_token,
    register_user,
    update_user,
)
from sonority.auth.schemas import (
    UserCreateSchema,
    UserLoginSchema,
    UserPasswordChangeSchema,
    UserUpdateSchema,
)
from tests.database import Session


def test_get_user_by_id(session: Session, registered_user: User):
    """
    Test that a user can be retrieved by id
    """
    user = get_user_by_id(session, registered_user.id)
    assert user is not None
    assert user.email == registered_user.email
    assert user.full_name == registered_user.full_name
    assert user.username == registered_user.username
    assert user.pwd_hash == registered_user.pwd_hash


def test_get_user_by_id_invalid_id(session: Session):
    """
    Test that a user cannot be retrieved by an invalid id
    """
    user = get_user_by_id(session, UUID("00000000-0000-0000-0000-000000000000"))
    assert user is None


def test_get_user_by_email(session: Session, registered_user: User):
    """
    Test that a user can be retrieved by email
    """
    user = get_user_by_email(session, registered_user.email)
    assert user is not None
    assert user.email == registered_user.email
    assert user.full_name == registered_user.full_name
    assert user.username == registered_user.username
    assert user.pwd_hash == registered_user.pwd_hash


def test_get_user_by_email_invalid_email(session: Session):
    """
    Test that a user cannot be retrieved by an invalid email
    """
    user = get_user_by_email(session, "incorrectemail@example.com")
    assert user is None


def test_get_user_by_username(session: Session, registered_user: User):
    """
    Test that a user can be retrieved by username
    """
    user = get_user_by_username(session, registered_user.username)
    assert user is not None
    assert user.email == registered_user.email
    assert user.full_name == registered_user.full_name
    assert user.username == registered_user.username
    assert user.pwd_hash == registered_user.pwd_hash


def test_get_user_by_username_invalid_username(session: Session):
    """
    Test that a user cannot be retrieved by an invalid username
    """
    user = get_user_by_username(session, "incorrectusername")
    assert user is None


def test_register_user(session: Session):
    """
    Test that a user can be registered
    """
    user_schema = UserCreateSchema(
        email="testemail@example.com",
        full_name="Test User",
        username="testuser",
        password="testpassword",
    )

    user = register_user(session, user_schema)
    assert user.email == user_schema.email
    assert user.full_name == user_schema.full_name
    assert user.username == user_schema.username
    assert user.pwd_hash is not None
    assert user.pwd_hash != user_schema.password

    db_user = get_user_by_id(session, user.id)
    assert db_user is not None
    assert db_user.email == user_schema.email
    assert db_user.full_name == user_schema.full_name
    assert db_user.username == user_schema.username
    assert db_user.pwd_hash is not None
    assert db_user.pwd_hash != user_schema.password


@pytest.fixture
def registered_user(session: Session):
    """
    Return a registered user
    """
    user_schema = UserCreateSchema(
        email="testemail@example.com",
        full_name="Test User",
        username="testuser",
        password="testpassword",
    )
    return register_user(session, user_schema)


def test_register_user_duplicate_email(session: Session, registered_user: User):
    """
    Test that a user cannot be registered with a duplicate email
    """
    user_schema = UserCreateSchema(
        email="testemail@example.com",
        full_name="Test User",
        username="testuser2",
        password="testpassword",
    )
    with pytest.raises(RegistrationError) as exc_info:
        register_user(session, user_schema)

    assert exc_info.value.args[0] == "email already in use"


def test_register_user_duplicate_username(session: Session, registered_user: User):
    """
    Test that a user cannot be registered with a duplicate username
    """
    user_schema = UserCreateSchema(
        email="testemail2@example.com",
        full_name="Test User",
        username="testuser",
        password="testpassword",
    )
    with pytest.raises(RegistrationError) as exc_info:
        register_user(session, user_schema)

    assert exc_info.value.args[0] == "username already in use"


def test_update_user(session: Session, registered_user: User):
    """
    Test that a user can be updated
    """
    user_schema = UserUpdateSchema(
        email="newtestemail@example.com",
        full_name="Test User 2",
        username="newtestuser",
    )
    user = update_user(session, registered_user, user_schema)
    assert user.email == user_schema.email
    assert user.full_name == user_schema.full_name
    assert user.username == user_schema.username

    db_user = get_user_by_id(session, user.id)
    assert db_user is not None
    assert db_user.email == user_schema.email
    assert db_user.full_name == user_schema.full_name
    assert db_user.username == user_schema.username


def test_update_user_duplicate_email(session: Session, registered_user: User):
    """
    Test that a user cannot be updated with a duplicate email
    """
    user_schema = UserCreateSchema(
        email="newtestemail@example.com",
        full_name="New Test User",
        username="newtestuser",
        password="newtestpassword",
    )
    register_user(session, user_schema)

    user_schema = UserUpdateSchema(
        email="newtestemail@example.com",
    )
    with pytest.raises(UserUpdateError) as exc_info:
        update_user(session, registered_user, user_schema)

    assert exc_info.value.args[0] == "email already in use"


def test_update_user_duplicate_username(session: Session, registered_user: User):
    """
    Test that a user cannot be updated with a duplicate username
    """
    user_schema = UserCreateSchema(
        email="newtestemail@example.com",
        full_name="New Test User",
        username="newtestuser",
        password="newtestpassword",
    )
    register_user(session, user_schema)

    user_schema = UserUpdateSchema(
        username="newtestuser",
    )
    with pytest.raises(UserUpdateError) as exc_info:
        update_user(session, registered_user, user_schema)

    assert exc_info.value.args[0] == "username already in use"


def test_delete_user(session: Session, registered_user: User):
    """
    Test that a user can be deleted
    """
    user_id = registered_user.id
    delete_user(session, registered_user)
    assert get_user_by_id(session, user_id) is None


def test_change_user_password(session: Session, registered_user: User):
    """
    Test that a user's password can be changed
    """
    user_schema = UserPasswordChangeSchema(
        old_password="testpassword",
        new_password="newtestpassword",
    )
    change_user_password(session, registered_user, user_schema)
    assert registered_user.pwd_hash is not None
    assert registered_user.pwd_hash != user_schema.old_password
    assert registered_user.pwd_hash != user_schema.new_password

    # Test that the new password works
    user_schema = UserLoginSchema(
        email="testemail@example.com",
        password="newtestpassword",
    )
    login_user(session, user_schema)


def test_change_user_password_same_password(session: Session, registered_user: User):
    """
    Test that a user's password cannot be changed to the same password
    """
    user_schema = UserPasswordChangeSchema(
        old_password="testpassword",
        new_password="testpassword",
    )
    with pytest.raises(PasswordChangeError) as exc_info:
        change_user_password(session, registered_user, user_schema)

    assert exc_info.value.args[0] == "New password cannot be the same as old password"


def test_change_user_password_incorrect_password(
    session: Session, registered_user: User
):
    """
    Test that a user's password cannot be changed with an incorrect password
    """
    user_schema = UserPasswordChangeSchema(
        old_password="wrongpassword",
        new_password="newtestpassword",
    )
    with pytest.raises(PasswordChangeError) as exc_info:
        change_user_password(session, registered_user, user_schema)

    assert exc_info.value.args[0] == "Incorrect password"


def test_login_user(session: Session, registered_user: User):
    """
    Test that a user can be logged in
    """
    user_schema = UserLoginSchema(
        email="testemail@example.com",
        password="testpassword",
    )
    user = login_user(session, user_schema)
    assert user.email == registered_user.email
    assert user.full_name == registered_user.full_name
    assert user.username == registered_user.username
    assert user.pwd_hash == registered_user.pwd_hash


def test_login_user_incorrect_password(session: Session, registered_user: User):
    """
    Test that a user cannot be logged in with an incorrect password
    """
    user_schema = UserLoginSchema(
        email="testemail@example.com",
        password="badtestpassword",
    )
    with pytest.raises(AuthenticationError) as exc_info:
        login_user(session, user_schema)

    assert exc_info.value.args[0] == "Incorrect password"


def test_login_user_incorrect_email(session: Session, registered_user: User):
    """
    Test that a user cannot be logged in with an incorrect email
    """
    user_schema = UserLoginSchema(
        email="incorrectemail@example.com",
        password="testpassword",
    )
    with pytest.raises(AuthenticationError) as exc_info:
        login_user(session, user_schema)

    assert exc_info.value.args[0] == "Email not found"


def test_login_user_from_token(session: Session, registered_user: User):
    """
    Test that a user can be logged in from a token
    """
    user_schema = UserLoginSchema(
        email="testemail@example.com",
        password="testpassword",
    )
    token = auth_token(session, user_schema)
    user = login_user_from_token(session, token)
    assert user.email == registered_user.email
    assert user.full_name == registered_user.full_name
    assert user.username == registered_user.username
    assert user.pwd_hash == registered_user.pwd_hash


def test_login_user_from_token_invalid_token(session: Session, registered_user: User):
    """
    Test that a user cannot be logged in from an invalid token
    """
    with pytest.raises(AuthenticationError) as exc_info:
        login_user_from_token(session, "invalidtoken")

    assert exc_info.value.args[0] == "Invalid token"


def test_login_user_from_token_deleted_user(session: Session, registered_user: User):
    """
    Test that a user cannot be logged in from a token if the user has been deleted
    """
    user_schema = UserLoginSchema(
        email="testemail@example.com",
        password="testpassword",
    )
    token = auth_token(session, user_schema)
    delete_user(session, registered_user)
    with pytest.raises(AuthenticationError) as exc_info:
        login_user_from_token(session, token)

    assert exc_info.value.args[0] == "User not found"
