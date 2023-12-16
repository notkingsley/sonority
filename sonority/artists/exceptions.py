class VerifiedArtistIsImmutable(Exception):
    """
    Raised when a verified artist is attempted to be modified.
    """

    pass


class ArtistNameInUse(Exception):
    """
    Raised when an artist name is already in use.
    """

    pass


class ArtistExists(Exception):
    """
    Raised when an artist already exists.
    """

    pass