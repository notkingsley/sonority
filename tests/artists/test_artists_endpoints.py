from uuid import UUID

from fastapi.testclient import TestClient

from tests import utils


def test_new_artist(client: TestClient):
    """
    Test creating a new artist
    """
    response = client.post(
        "/artists/new",
        json={
            "name": "Test Artist",
            "description": "Test Description",
        },
    )
    assert response.status_code == 201

    response_json = response.json()
    assert "id" in response_json
    assert response_json == {
        "id": response_json["id"],
        "name": "Test Artist",
        "description": "Test Description",
        "is_verified": False,
        "follower_count": 0,
    }


def test_new_artist_already_exists(artist_client: TestClient):
    """
    Test creating an artist that already exists
    """
    response = artist_client.post(
        "/artists/new",
        json={
            "name": "Test Artist",
            "description": "Test Description",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Artist already exists"}


def test_new_artist_name_in_use(artist_client: TestClient):
    """
    Test creating an artist with a name that is already in use
    """
    client = utils.create_randomized_test_client()
    response = client.post(
        "/artists/new",
        json={
            "name": "Test Artist",
            "description": "Test Description",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Artist name is already in use"}


def test_get_artist_by_id(artist_client: TestClient):
    """
    Test getting an artist by ID
    """
    artist_id = artist_client.get("/artists/me").json()["id"]
    client = utils.create_randomized_test_client()
    response = client.get(f"/artists?id={artist_id}")
    assert response.status_code == 200

    response_json = response.json()
    assert "id" in response_json
    assert response_json == {
        "id": artist_id,
        "name": "Test Artist",
        "description": "Test Description",
        "is_verified": False,
        "follower_count": 0,
    }


def test_get_artist_by_id_not_found(client: TestClient):
    """
    Test getting an artist by ID that does not exist
    """
    response = client.get(f"/artists?id={UUID('00000000-0000-0000-0000-000000000000')}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}

    response = client.get("/artists?id=invalidid")
    assert response.status_code == 422


def test_get_artist_by_name(artist_client: TestClient):
    """
    Test getting an artist by name
    """
    client = utils.create_randomized_test_client()
    response = client.get("/artists?name=Test Artist")
    assert response.status_code == 200

    response_json = response.json()
    assert "id" in response_json
    assert response_json == {
        "id": response_json["id"],
        "name": "Test Artist",
        "description": "Test Description",
        "is_verified": False,
        "follower_count": 0,
    }


def test_get_artist_by_name_not_found(client: TestClient):
    """
    Test getting an artist by name that does not exist
    """
    response = client.get("/artists?name=Bad Test Artist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


def test_get_artist_by_id_and_name(client: TestClient):
    """
    Test getting an artist by ID and name
    """
    response = client.get(f"/artists?id={UUID('00000000-0000-0000-0000-000000000000')}&name=Test Artist")
    assert response.status_code == 400
    assert response.json() == {"detail": "Only one of id or name can be provided"}


def test_get_artist_me(artist_client: TestClient):
    """
    Test getting the current user's artist profile
    """
    response = artist_client.get("/artists/me")
    assert response.status_code == 200

    response_json = response.json()
    assert "id" in response_json
    assert response_json == {
        "id": response_json["id"],
        "name": "Test Artist",
        "description": "Test Description",
        "is_verified": False,
        "follower_count": 0,
    }


def test_get_artist_me_not_found(client: TestClient):
    """
    Test getting the current user's artist profile when it does not exist
    """
    response = client.get("/artists/me")
    assert response.status_code == 403
    assert response.json() == {"detail": "User is not an artist"}


def test_update_artist(artist_client: TestClient):
    """
    Test updating an artist
    """
    response = artist_client.patch(
        "/artists/me",
        json={
            "name": "Test Artist 2",
            "description": "Test Description 2",
        },
    )
    assert response.status_code == 200

    response_json = response.json()
    assert "id" in response_json
    assert response_json == {
        "id": response_json["id"],
        "name": "Test Artist 2",
        "description": "Test Description 2",
        "is_verified": False,
        "follower_count": 0,
    }


def test_update_artist_name_in_use(artist_client: TestClient):
    """
    Test updating an artist with a name that is already in use
    """
    artist_client2 = utils.create_randomized_test_artist_client()
    response = artist_client2.patch(
        "/artists/me",
        json={
            "name": "Test Artist",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Artist name is already in use"}


def test_update_artist_name_verified(artist_client: TestClient):
    artist_client.post("/artists/me/verify")
    response = artist_client.patch(
        "/artists/me",
        json={
            "name": "Test Artist 2",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Cannot change name of verified artist"}


def test_delete_artist(artist_client: TestClient):
    """
    Test deleting an artist
    """
    artist_id = artist_client.get("/artists/me").json()["id"]
    response = artist_client.delete("/artists/me")
    assert response.status_code == 204
    assert response.content == b""

    response = artist_client.get("/artists/me")
    assert response.status_code == 403
    assert response.json() == {"detail": "User is not an artist"}

    response = artist_client.get(f"/artists?id={artist_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Artist not found"}


def test_delete_artist_not_found(client: TestClient):
    """
    Test deleting an artist that does not exist
    """
    response = client.delete("/artists/me")
    assert response.status_code == 403
    assert response.json() == {"detail": "User is not an artist"}


def test_verify_artist(artist_client: TestClient):
    """
    Test verifying an artist
    """
    response = artist_client.post("/artists/me/verify")
    assert response.status_code == 200

    response_json = response.json()
    assert "id" in response_json
    assert response_json == {
        "id": response_json["id"],
        "name": "Test Artist",
        "description": "Test Description",
        "is_verified": True,
        "follower_count": 0,
    }