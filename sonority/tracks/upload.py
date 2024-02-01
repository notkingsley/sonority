"""
This file implements a file upload functionality.

Currently, it simply saves the file to the local filesystem.
"""
from pathlib import Path
from uuid import UUID, uuid4


def upload_file(file: bytes, parent_dir: Path) -> UUID:
    """
    Save the file to the local filesystem.

    :param file: The file to save.
    :param parent_dir: The directory in which to save the file.
    :return: The UUID to retrieve the file.
    """
    file_id = uuid4()
    parent_dir.mkdir(parents=True, exist_ok=True)
    file_path = parent_dir / file_id.hex
    file_path.write_bytes(file)
    return file_id


def get_file(file_id: UUID, parent_dir: Path) -> Path:
    """
    Get the path to the file on the local filesystem.

    :param file_id: The UUID of the file.
    :param parent_dir: The directory in which the file is saved.
    :return: The file.
    """
    return parent_dir / file_id.hex


def delete_file(file_id: UUID, parent_dir: Path) -> None:
    """
    Delete the file from the local filesystem.

    :param file_id: The UUID of the file.
    :param parent_dir: The directory in which the file is saved.
    """
    get_file(file_id, parent_dir).unlink()
