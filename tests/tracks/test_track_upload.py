from uuid import UUID

import pytest

from sonority.tracks.upload import delete_file, get_file, upload_file
from tests import settings


@pytest.fixture(scope="function")
def uploaded_file_id():
    """
    Return an uploaded file ID.
    """
    file = b"test"
    return upload_file(file, settings.TEST_TRACKS_DIR)


def test_upload_file():
    """
    Test uploading a file.
    """
    contents = b"test"
    file_id = upload_file(contents, settings.TEST_TRACKS_DIR)
    file = get_file(file_id, settings.TEST_TRACKS_DIR)
    assert file.exists()
    assert file.read_bytes() == contents


def test_get_file(uploaded_file_id: UUID):
    """
    Test getting a file.
    """
    file = get_file(uploaded_file_id, settings.TEST_TRACKS_DIR)
    assert file.exists()
    assert file.read_bytes() == b"test"


def test_delete_file(uploaded_file_id: UUID):
    """
    Test deleting a file.
    """
    delete_file(uploaded_file_id, settings.TEST_TRACKS_DIR)
    file = get_file(uploaded_file_id, settings.TEST_TRACKS_DIR)
    assert not file.exists()
