from uuid import UUID

from fastapi.testclient import TestClient
import pytest

from tests import utils


def test_register_user(raw_client: TestClient):
    """
    Test that a user can be registered
    """
    data = {
        "username": "testuser",
        "email": "testemail@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
    response = raw_client.post("/users/register", json=data)
    assert response.status_code == 201
    assert "id" in response.json()
    data.pop("password")
    assert response.json() == {
        "id": response.json()["id"],
        **data,
    }


@pytest.fixture(scope="function")
def registered_user(raw_client: TestClient):
    """
    Register a user for use in other tests
    """
    data = {
        "username": "testuser",
        "email": "testemail@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
    raw_client.post("/users/register", json=data)


def test_register_user_duplicate_email(raw_client: TestClient, registered_user: None):
    """
    Test that a user cannot be registered with a duplicate email
    """
    data = {
        "username": "newtestuser",
        "email": "testemail@example.com",
        "password": "testpassword",
        "full_name": "New Test User",
    }
    response = raw_client.post("/users/register", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "email already in use"}


def test_register_user_duplicate_username(
    raw_client: TestClient, registered_user: None
):
    """
    Test that a user cannot be registered with a duplicate username
    """
    data = {
        "username": "testuser",
        "email": "newtestemail@example.com",
        "password": "testpassword",
        "full_name": "New Test User",
    }
    response = raw_client.post("/users/register", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "username already in use"}


def test_login_user(raw_client: TestClient, registered_user: None):
    """
    Test that a user can log in
    """
    data = {
        "username": "testemail@example.com",
        "password": "testpassword",
    }
    response = raw_client.post("/users/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"].lower() == "bearer"


def test_login_user_incorrect_password(raw_client: TestClient, registered_user: None):
    """
    Test that a user cannot login with an incorrect password
    """
    data = {
        "username": "testemail@example.com",
        "password": "incorrectpassword",
    }
    response = raw_client.post("/users/login", data=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_login_user_incorrect_email(raw_client: TestClient, registered_user: None):
    """
    Test that a user cannot login with an incorrect email
    """
    data = {
        "username": "incorrectemail@example.com",
        "password": "testpassword",
    }
    response = raw_client.post("/users/login", data=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_login_user_username_not_email(raw_client: TestClient, registered_user: None):
    """
    Test that a user cannot login with a username that is not an email
    """
    data = {
        "username": "testuser",
        "password": "testpassword",
    }
    response = raw_client.post("/users/login", data=data)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]


def test_login_user_invalid_email(raw_client: TestClient, registered_user: None):
    """
    Test that a user cannot login with an invalid email
    """
    data = {
        "username": "invalidemail",
        "password": "testpassword",
    }
    response = raw_client.post("/users/login", data=data)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]


def test_get_user(client: TestClient):
    """
    Test that a user can be retrieved by id
    """
    user_id = client.get("/users/me").json()["id"]
    client2 = utils.create_randomized_test_client()
    response = client2.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "username": "testuser",
        "email": "testemail@example.com",
        "full_name": "Test User",
    }


def test_get_user_not_found(raw_client: TestClient):
    """
    Test that a user cannot be retrieved by an invalid id
    """
    response = raw_client.get(f"/users/{UUID('00000000-0000-0000-0000-000000000000')}")
    assert response.status_code == 404
    assert response.json() == {"detail": "user not found"}

    response = raw_client.get(f"/users/invalidid")
    assert response.status_code == 422


def test_get_user_me(client: TestClient):
    """
    Test that the current user can be retrieved
    """
    response = client.get("/users/me")
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json() == {
        "id": response.json()["id"],
        "username": "testuser",
        "email": "testemail@example.com",
        "full_name": "Test User",
    }


def test_update_user_username(client: TestClient):
    """
    Test that the current user's username can be updated
    """
    data = {
        "username": "newtestuser",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json() == {
        "id": response.json()["id"],
        "username": "newtestuser",
        "email": "testemail@example.com",
        "full_name": "Test User",
    }


def test_update_user_email(client: TestClient):
    """
    Test that the current user's email can be updated
    """
    data = {
        "email": "newtestemail@example.com",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json() == {
        "id": response.json()["id"],
        "username": "testuser",
        "email": "newtestemail@example.com",
        "full_name": "Test User",
    }


def test_update_user_full_name(client: TestClient):
    """
    Test that the current user's full name can be updated
    """
    data = {
        "full_name": "New Test User",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json() == {
        "id": response.json()["id"],
        "username": "testuser",
        "email": "testemail@example.com",
        "full_name": "New Test User",
    }


def test_update_user_all(client: TestClient):
    """
    Test that the current user's username, email, and full name can be updated
    """
    data = {
        "username": "newtestuser",
        "email": "newtestemail@example.com",
        "full_name": "New Test User",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json() == {
        "id": response.json()["id"],
        "username": "newtestuser",
        "email": "newtestemail@example.com",
        "full_name": "New Test User",
    }


def test_update_user_duplicate_username(client: TestClient):
    """
    Test that the current user's username cannot be updated to a duplicate
    """
    data = {
        "username": "testuser2",
        "email": "testemail2@example.com",
        "password": "testpassword",
        "full_name": "Test User 2",
    }
    client.post("/users/register", json=data)

    data = {
        "username": "testuser2",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "username already in use"}


def test_update_user_duplicate_email(client: TestClient):
    """
    Test that the current user's email cannot be updated to a duplicate
    """
    data = {
        "username": "testuser2",
        "email": "testemail2@example.com",
        "password": "testpassword",
        "full_name": "Test User 2",
    }
    client.post("/users/register", json=data)

    data = {
        "email": "testemail2@example.com",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "email already in use"}


def test_update_user_invalid_email(client: TestClient):
    """
    Test that the current user's email cannot be updated to an invalid email
    """
    data = {
        "email": "invalidemail",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]

    data = {
        "email": "invalidemail@example",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]

    data = {
        "email": "invalidemail.com",
    }
    response = client.patch("/users/me", json=data)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]


def test_delete_user(client: TestClient):
    """
    Test that the current user can be deleted
    """
    id = client.get("/users/me").json()["id"]

    response = client.delete("/users/me")
    assert response.status_code == 204
    assert response.text == ""

    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    response = client.get(f"/users/{id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "user not found"}


def test_change_user_password(client: TestClient):
    """
    Test that the current user's password can be changed
    """
    data = {
        "old_password": "testpassword",
        "new_password": "newtestpassword",
    }
    response = client.patch("/users/me/password", json=data)
    assert response.status_code == 204
    assert response.text == ""

    data = {
        "username": "testemail@example.com",
        "password": "newtestpassword",
    }
    response = client.post("/users/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"].lower() == "bearer"

    data = {
        "username": "testemail@example.com",
        "password": "testpassword",
    }
    response = client.post("/users/login", data=data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_change_user_password_same(client: TestClient):
    """
    Test that the current user's password cannot be changed to the same password
    """
    data = {
        "old_password": "testpassword",
        "new_password": "testpassword",
    }
    response = client.patch("/users/me/password", json=data)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "New password cannot be the same as old password"
    }


def test_change_user_password_incorrect_old(client: TestClient):
    """
    Test that the current user's password cannot be changed with an incorrect old password
    """
    data = {
        "old_password": "incorrectpassword",
        "new_password": "newtestpassword",
    }
    response = client.patch("/users/me/password", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect password"}

    data = {
        "username": "testemail@example.com",
        "password": "testpassword",
    }
    response = client.post("/users/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"].lower() == "bearer"
