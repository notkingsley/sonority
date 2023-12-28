class AlbumNameInUse(Exception):
    """
    Exception raised when an album name is already in use
    """

    pass


class ReleasedAlbumIsImmutable(Exception):
    """
    Exception raised when a released album is modified
    """

    pass


class AlbumAlreadyReleased(Exception):
    """
    Exception raised when an album is already released
    """

    pass