from fastapi.testclient import TestClient
import pytest

from tests import utils
from tests.utils import (
    DEFAULT_ALBUM_CREATE_INFO,
    DEFAULT_RELEASED_ALBUM_INFO,
    DEFAULT_UNRELEASED_ALBUM_INFO,
)


def test_new_album(artist_client: TestClient):
    """
    Test creating a new album
    """
    response = artist_client.post("/albums/new", json=DEFAULT_ALBUM_CREATE_INFO)
    assert response.status_code == 201
    assert response.json() == {**DEFAULT_UNRELEASED_ALBUM_INFO}


@pytest.fixture(scope="function")
def client_local(artist_with_album_client: TestClient):
    """
    Shortcut for artist_with_album_client in this file
    """
    return artist_with_album_client


def test_new_album_name_in_use(client_local: TestClient):
    """
    Test creating a new album with a name that is already in use
    """
    response = client_local.post("/albums/new", json=DEFAULT_ALBUM_CREATE_INFO)
    assert response.status_code == 409
    assert response.json() == {"detail": "Album name is already in use"}


def test_new_album_name_in_use_different_artist(client_local: TestClient):
    """
    Test creating a new album with a name that is already in use by a different artist
    """
    client2 = utils.create_randomized_test_artist_client()
    response = client2.post("/albums/new", json=DEFAULT_ALBUM_CREATE_INFO)
    assert response.status_code == 201
    assert response.json() == {**DEFAULT_UNRELEASED_ALBUM_INFO}


def test_update_album_name(client_local: TestClient):
    """
    Test updating an album with a new name
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    response = client_local.patch(
        f"/albums/{album_id}", json={"name": "New Test Album"}
    )
    assert response.status_code == 200
    assert response.json() == {
        **DEFAULT_UNRELEASED_ALBUM_INFO,
        "name": "New Test Album",
        "id": album_id,
    }


def test_update_album_name_in_use(client_local: TestClient):
    """
    Test updating an album with a name that is already in use
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    new_album_info = utils.create_randomized_test_album_for_artist_client(client_local)
    response = client_local.patch(
        f"/albums/{album_id}", json={"name": new_album_info["name"]}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Album name is already in use"}


def test_update_album_name_in_use_different_artist(client_local: TestClient):
    """
    Test updating an album with a name that is already in use by a different artist
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    client2 = utils.create_randomized_test_artist_client()
    new_album_info = utils.create_randomized_test_album_for_artist_client(client2)
    response = client_local.patch(
        f"/albums/{album_id}", json={"name": new_album_info["name"]}
    )
    assert response.status_code == 200
    assert response.json() == {
        **DEFAULT_UNRELEASED_ALBUM_INFO,
        "name": new_album_info["name"],
        "id": album_id,
    }


def test_update_album_type(client_local: TestClient):
    """
    Test updating an album with a new type
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    response = client_local.patch(f"/albums/{album_id}", json={"album_type": "single"})
    assert response.status_code == 200
    assert response.json() == {
        **DEFAULT_UNRELEASED_ALBUM_INFO,
        "name": response.json()["name"],
        "album_type": "single",
        "id": album_id,
    }


def test_update_album_released(client_local: TestClient):
    """
    Test updating a released album
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    client_local.post(f"/albums/{album_id}/release")
    response = client_local.patch(
        f"/albums/{album_id}", json={"name": "New Test Album"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Released albums cannot be modified"}


def test_delete_album(client_local: TestClient):
    """
    Test deleting an album
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    response = client_local.delete(f"/albums/{album_id}")
    assert response.status_code == 204
    assert response.text == ""

    response = client_local.get(f"/albums/{album_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Album does not exist"}


def test_release_album(client_local: TestClient):
    """
    Test releasing an album
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    response = client_local.post(f"/albums/{album_id}/release")
    assert response.status_code == 200
    assert response.json() == {
        **DEFAULT_RELEASED_ALBUM_INFO,
        "name": response.json()["name"],
        "id": album_id,
    }


def test_release_album_already_released(client_local: TestClient):
    """
    Test releasing an album that is already released
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    client_local.post(f"/albums/{album_id}/release")
    response = client_local.post(f"/albums/{album_id}/release")
    assert response.status_code == 409
    assert response.json() == {"detail": "Album is already released"}


def test_get_album(client_local: TestClient):
    """
    Test getting an album by ID
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    client_local.post(f"/albums/{album_id}/release")
    response = client_local.get(f"/albums/{album_id}")
    assert response.status_code == 200
    assert response.json() == {
        **DEFAULT_RELEASED_ALBUM_INFO,
        "id": album_id,
        "name": response.json()["name"],
    }


def test_get_unreleased_album(client_local: TestClient):
    """
    Test getting an unreleased album by ID
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    response = client_local.get(f"/albums/drafts/{album_id}")
    assert response.status_code == 200
    assert response.json() == {
        **DEFAULT_UNRELEASED_ALBUM_INFO,
        "id": album_id,
        "name": response.json()["name"],
    }


def test_get_released_album_as_unreleased(client_local: TestClient):
    """
    Test getting a released album as an unreleased album
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    client_local.post(f"/albums/{album_id}/release")
    response = client_local.get(f"/albums/drafts/{album_id}", follow_redirects=False)
    assert response.status_code == 307
    assert response.is_redirect
    assert response.has_redirect_location
    assert response.headers["location"] == f"/albums/{album_id}"


def test_get_unreleased_album_as_released(client_local: TestClient):
    """
    Test getting an unreleased album as a released album
    """
    album_id = utils.create_randomized_test_album_for_artist_client(client_local)["id"]
    response = client_local.get(f"/albums/{album_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Album does not exist"}


def test_get_unreleased_albums(artist_client: TestClient):
    """
    Test getting all unreleased albums
    """
    id1 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id2 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id3 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id4 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    artist_client.post(f"/albums/{id1}/release")
    artist_client.post(f"/albums/{id3}/release")

    response = artist_client.get("/albums/drafts")
    assert response.status_code == 200
    assert response.json() == [
        {
            **DEFAULT_UNRELEASED_ALBUM_INFO,
            "id": id4,
            "name": response.json()[0]["name"],
        },
        {
            **DEFAULT_UNRELEASED_ALBUM_INFO,
            "id": id2,
            "name": response.json()[1]["name"],
        },
    ]


def test_get_released_albums(artist_client: TestClient):
    """
    Test getting all released albums
    """
    id1 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id2 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id3 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id4 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    artist_client.post(f"/albums/{id1}/release")
    artist_client.post(f"/albums/{id3}/release")

    response = artist_client.get("/albums/mine")
    assert response.status_code == 200
    assert response.json() == [
        {**DEFAULT_RELEASED_ALBUM_INFO, "id": id1, "name": response.json()[0]["name"]},
        {**DEFAULT_RELEASED_ALBUM_INFO, "id": id3, "name": response.json()[1]["name"]},
    ]


def test_get_all_albums_by_artist(artist_client: TestClient):
    """ 
    Test getting all albums by an artist
    """
    id1 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id2 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id3 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    id4 = utils.create_randomized_test_album_for_artist_client(artist_client)["id"]
    artist_id = artist_client.get("/artists/me").json()["id"]
    artist_client.post(f"/albums/{id1}/release")
    artist_client.post(f"/albums/{id3}/release")

    client = utils.create_randomized_test_client()
    response = client.get(f"/albums/by/{artist_id}")
    assert response.status_code == 200
    assert response.json() == [
        {**DEFAULT_RELEASED_ALBUM_INFO, "id": id1, "name": response.json()[0]["name"]},
        {**DEFAULT_RELEASED_ALBUM_INFO, "id": id3, "name": response.json()[1]["name"]},
    ]
